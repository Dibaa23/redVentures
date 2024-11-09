const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const cors = require('cors');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config({ path: path.resolve(__dirname, '../.env') });

console.log('Environment Check:');
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('PORT:', process.env.PORT);
console.log('OPENAI_API_KEY exists:', !!process.env.OPENAI_API_KEY);

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS in development
if (process.env.NODE_ENV !== 'production') {
  app.use(cors());
}

app.use(express.json());

// Always serve the static files from the build directory
app.use(express.static(path.join(__dirname, '../dashboard/build')));

// Serve exported_results based on environment
app.use('/exported_results', express.static(
  path.join(__dirname, '../dashboard/public/exported_results')
));

app.post('/api/generate-insights', async (req, res) => {
  console.log('Starting Python script...');
  console.log('Environment:', process.env.NODE_ENV);
  
  // Get absolute paths
  const scriptPath = path.resolve(__dirname, '../data_processing/generate_insights.py');
  console.log('Python script path:', scriptPath);

  // Determine Python command based on environment
  const pythonCommand = process.env.NODE_ENV === 'production' ? 'python3' : 'python';

  const pythonProcess = spawn(pythonCommand, [scriptPath], {
    cwd: path.resolve(__dirname, '../data_processing'),
    env: {
      ...process.env, // Pass all environment variables to Python
      PYTHONUNBUFFERED: '1' // Ensure Python output isn't buffered
    }
  });

  let dataReceived = '';
  let errorReceived = '';

  pythonProcess.stdout.on('data', (data) => {
    dataReceived += data.toString();
    console.log('Python output:', data.toString());
  });

  pythonProcess.stderr.on('data', (data) => {
    errorReceived += data.toString();
    console.error('Python error:', data.toString());
  });

  pythonProcess.on('error', (error) => {
    console.error('Failed to start Python process:', error);
    res.status(500).json({ 
      error: 'Failed to start Python process',
      details: error.message
    });
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    console.log('Full output:', dataReceived);
    
    if (errorReceived) {
      console.error('Full errors:', errorReceived);
    }

    if (code !== 0) {
      return res.status(500).json({ 
        error: 'Failed to generate insights',
        details: errorReceived || 'No error details available'
      });
    }

    // Check if the file was actually created
    const outputPath = path.join(
      __dirname, 
      '../dashboard/public/exported_results/call_3_result.txt'
    );

    if (!require('fs').existsSync(outputPath)) {
      return res.status(500).json({ 
        error: 'Output file not created',
        details: 'The Python script completed but did not create the output file'
      });
    }

    res.json({ 
      success: true,
      output: dataReceived
    });
  });
});

// API routes
app.get('/api/test', (req, res) => {
  res.json({ message: 'API is working' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    details: process.env.NODE_ENV === 'production' ? 'An error occurred' : err.message
  });
});

// This should be the LAST route
app.get('*', (req, res) => {
  console.log('Serving index.html for path:', req.path);
  res.sendFile(path.join(__dirname, '../dashboard/build/index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`);
  console.log('Current directory:', __dirname);
  console.log('Build path:', path.join(__dirname, '../dashboard/build'));
  console.log('Public path:', path.join(__dirname, '../dashboard/public'));
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('Unhandled Rejection:', err);
  if (process.env.NODE_ENV === 'production') {
    process.exit(1);
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  if (process.env.NODE_ENV === 'production') {
    process.exit(1);
  }
});