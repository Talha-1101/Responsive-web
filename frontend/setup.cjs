#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Setting up Responsive Website Tester Frontend...\n');

function createDirectory(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`✅ Created ${dir}/`);
  }
}

function createFile(filePath, content) {
  const dir = path.dirname(filePath);
  createDirectory(dir);
  fs.writeFileSync(filePath, content);
  console.log(`✅ Created ${filePath}`);
}

// Create required directories
const directories = [
  'public',
  'src/components/ui',
  'src/components/analysis',
  'src/components/layout',
  'src/pages',
  'src/hooks',
  'src/services',
  'src/types',
  'src/utils'
];

directories.forEach(createDirectory);

// Create public files
createFile('public/robots.txt', 'User-agent: *\nAllow: /');

// Check if we need to install dependencies
if (!fs.existsSync('node_modules')) {
  console.log('\n📦 Installing dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✅ Dependencies installed successfully');
  } catch (error) {
    console.log('⚠️  Please run "npm install" manually');
  }
}

console.log('\n🎉 Frontend setup complete!');
console.log('\n🚀 To start the development server:');
console.log('   npm run dev');
console.log('\n📖 The app will be available at: http://localhost:3000');
console.log('\n💡 Make sure the backend is running on port 8000');
console.log('💡 Clear your browser cache if you see any issues');