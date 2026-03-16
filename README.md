# DeepShield Demo - Full Stack Application

A research demonstration website for **DeepShield: Proactive Defense Against Deepfake Generation**.

DeepShield is an academic research project that protects facial images from being misused by deepfake generation models through adversarial perturbation techniques.

## 🏗️ Project Structure

```
deepshield-demo/
├── frontend/               # React frontend (Vite)
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Header.jsx
│   │   │   ├── ImageUpload.jsx
│   │   │   ├── ResultVisualization.jsx
│   │   │   ├── MetricsDisplay.jsx
│   │   │   └── ProcessingSteps.jsx
│   │   ├── services/      # API services
│   │   │   └── api.js
│   │   ├── App.jsx        # Main app component
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/               # Node.js + Express backend
│   ├── src/
│   │   ├── routes/       # API routes
│   │   │   └── image.routes.js
│   │   ├── controllers/  # Request handlers
│   │   │   └── image.controller.js
│   │   ├── services/     # Business logic
│   │   │   └── deepshield.service.js
│   │   ├── middleware/   # Middleware
│   │   │   └── upload.middleware.js
│   │   └── server.js     # Express app
│   ├── uploads/          # Uploaded images storage
│   ├── package.json
│   └── .env
│
└── README.md
```

## 🚀 Features

### Frontend
- ✅ Modern React UI with Vite
- ✅ Drag-and-drop image upload
- ✅ Real-time processing status
- ✅ Side-by-side result comparison
- ✅ Detailed metrics visualization
- ✅ Responsive design

### Backend
- ✅ Express.js REST API
- ✅ Multer file upload handling
- ✅ Image processing with Sharp
- ✅ Simulated adversarial perturbation
- ✅ Simulated deepfake generation
- ✅ Comprehensive metrics calculation

## 📋 Prerequisites

- **Node.js** 16+ and npm
- Modern web browser

## 🛠️ Installation & Setup

### 1. Clone/Download the Project

```bash
cd deepshield-demo
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Start the backend server
npm run dev
```

The backend will run on `http://localhost:5000`

**Backend Dependencies:**
- express
- cors
- multer (file upload)
- sharp (image processing)
- dotenv
- uuid

### 3. Frontend Setup

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173`

**Frontend Dependencies:**
- react
- react-dom
- axios
- vite

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## 🎯 Usage

### Complete Workflow

1. **Upload Image**: Drag and drop or select a facial image
2. **Process**: Click "Protect Image with DeepShield"
3. **View Results**: See the comparison between:
   - Original image
   - Protected image (with adversarial noise)
   - Deepfake from original (successful)
   - Deepfake from protected (failed/disrupted)
4. **Analyze Metrics**: Review protection effectiveness and visual quality metrics

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```

### Upload Image
```
POST /api/images/upload
Content-Type: multipart/form-data
Body: { image: File }
```

### Protect Image
```
POST /api/images/protect
Content-Type: application/json
Body: { filename: string }
```

### Simulate Deepfake
```
POST /api/images/simulate-deepfake
Content-Type: application/json
Body: { filename: string, isProtected: boolean }
```

### Complete Workflow (Recommended)
```
POST /api/images/process-complete
Content-Type: multipart/form-data
Body: { image: File }

Returns: {
  original: { url, filename },
  protected: { url, metrics },
  deepfakeFromOriginal: { url, metrics },
  deepfakeFromProtected: { url, metrics },
  comparisonMetrics: { ... }
}
```

## 📊 Metrics Explained

### Visual Quality Metrics (Protected Image)
- **PSNR**: Peak Signal-to-Noise Ratio (higher = better quality)
- **SSIM**: Structural Similarity Index (higher = more similar to original)
- **LPIPS**: Learned Perceptual Image Patch Similarity (lower = less perceptual difference)
- **Frequency Rate**: Concentration of noise in low-frequency bands

### Defense Effectiveness Metrics
- **Identity Similarity**: How well deepfake matches the target (lower = better defense)
- **L2 Distance**: Pixel-level distortion in deepfake output
- **PSNR Defense**: Quality degradation in deepfake output
- **Protection Success Rate**: Percentage of successful defense

## 🧪 Simulation Details

This demo **simulates** the DeepShield algorithm for demonstration purposes:

### Protection Simulation
- Adds subtle noise overlay to simulate adversarial perturbations
- Maintains visual quality (PSNR ~38 dB, LPIPS ~0.01)

### Deepfake Simulation
- **Unprotected**: Applies slight modifications (simulating successful deepfake)
- **Protected**: Applies heavy blur and distortion (simulating failed deepfake)

### Actual Implementation
In a production research environment, this would:
- Use actual DeepShield optimization algorithm (trajectory-based surrogate attack)
- Apply real adversarial perturbations optimized against face recognition models
- Test against actual deepfake models (DiffFace, FaceSwap, etc.)

## 🔧 Configuration

### Backend (.env)
```
PORT=5000
NODE_ENV=development
CORS_ORIGIN=http://localhost:5173
```

### Frontend (vite.config.js)
The frontend proxies API calls to the backend automatically.

## 📁 File Storage

Uploaded and processed images are stored in:
```
backend/uploads/
```

Files are served statically at:
```
http://localhost:5000/uploads/{filename}
```

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 or 5173 is already in use:

**Backend:**
```bash
# Change PORT in backend/.env
PORT=5001
```

**Frontend:**
```bash
# Change port in frontend/vite.config.js
server: { port: 5174 }
```

### CORS Issues
Ensure backend `.env` has correct `CORS_ORIGIN`:
```
CORS_ORIGIN=http://localhost:5173
```

### Image Upload Fails
Check:
- File size < 10MB
- File is an image (jpg, png, gif, webp)
- `backend/uploads/` directory exists

### Sharp Installation Issues
If Sharp fails to install:
```bash
npm install --platform=linux --arch=x64 sharp
```

## 🎨 Customization

### Styling
All styles are in `frontend/src/index.css`. The design uses:
- CSS custom properties (variables)
- Material Symbols icons
- Inter font family
- Responsive grid layouts

### Processing Algorithm
Modify `backend/src/services/deepshield.service.js` to:
- Adjust noise intensity
- Change blur/distortion levels
- Modify metrics calculation

## 📚 Research Context

This demo is based on the research paper:
**"DeepShield: Proactive Defense Against Deepfake Generation"**

### Key Concepts
- **Trajectory-Based Surrogate Attack**: Attacks the diffusion denoising process
- **Dual Dynamic Anti-Anchors**: Multi-directional identity disruption
- **Semantic-Aware Spatial Guidance**: Focuses perturbations on identity-critical regions
- **Perceptual Quality Constraint**: Maintains visual imperceptibility

### Tested Against
- DiffFace
- FaceAdapter
- ReFace
- DiffSwap
- CanonSwap

## 📄 License

MIT License - Academic Research Project

## 🙏 Acknowledgment

Research funded by Ho Chi Minh University of Education Foundation for Science and Technology.

---

**Note**: This is a demonstration tool for academic research purposes. The actual DeepShield algorithm involves sophisticated optimization techniques and should be implemented with proper face recognition models and deepfake generators for production use.