# Instagram Message Analyzer

A comprehensive web application to analyze your Instagram messaging patterns, social network, and communication habits.

## 🌟 Features

### 📊 **Message Analysis**
- Total messages, % sent/received
- First/Last message date
- Average message length
- Top 10 words used (excluding stopwords)
- Message timing breakdown (hourly, weekly, by day part)

### ⏱️ **Response Time Analysis**
- Average/median response time
- Fastest/slowest replies
- Response categorization (instant, quick, slow, etc.)
- Conversation gaps with dates

### 😊 **Emoji Analysis**
- Top 10 most common emojis
- Emoji usage patterns
- Emoji comparison between friends

### 📱 **Post Sharing Analysis**
- Instagram post/reel sharing detection
- Post sharing count and patterns

### 🌐 **Social Network Insights**
- Friendship rankings by activity
- Most balanced vs. one-sided friendships
- Longest friendships
- Fastest response friends
- Friendship categories (Best Friends, Close Friends, Regular, Distant)

## 🚀 Quick Start

### Frontend (React + Vite)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

### Backend (Flask)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Flask server:**
   ```bash
   python app.py
   ```

## 🛠️ Tech Stack

### Frontend
- **React 18** with Vite
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **Recharts** for data visualization
- **React Router** for navigation
- **Axios** for API calls
- **React Dropzone** for file uploads

### Backend
- **Flask** with CORS support
- **Python** for data processing
- **Emoji library** for emoji detection
- **JSON processing** for Instagram data

## 📁 Project Structure

```
instagram-analyzer/
├── src/
│   ├── components/          # Reusable components
│   ├── contexts/           # React contexts
│   ├── pages/              # Page components
│   ├── App.jsx             # Main app component
│   └── main.jsx            # Entry point
├── backend/
│   ├── app.py              # Flask API
│   └── requirements.txt    # Python dependencies
├── package.json            # Frontend dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
└── vercel.json             # Deployment config
```

## 🌐 API Endpoints

- `POST /api/upload` - Upload Instagram data ZIP
- `GET /api/friends` - Get list of friends
- `GET /api/analysis/<friend_id>` - Get detailed friend analysis
- `GET /api/network` - Get social network insights
- `GET /api/health` - Health check

## 🎨 Features

### **Responsive Design**
- Mobile-first approach
- Tablet and desktop optimized
- Dark mode support

### **Data Visualization**
- Interactive charts and graphs
- Real-time data updates
- Animated transitions

### **User Experience**
- Drag & drop file upload
- Loading states and progress indicators
- Error handling and validation
- Toast notifications

### **Privacy & Security**
- Local data processing
- No permanent data storage
- Session-based analysis
- Secure file handling

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Configure build settings
3. Deploy automatically on push

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`

## 📱 How to Use

1. **Get your Instagram data:**
   - Go to Instagram Settings → Privacy and Security → Data Download
   - Request your data and wait for the email
   - Download the ZIP file and extract it

2. **Choose your upload method:**

   **Option 1: Messages Folder (Recommended)**
   - Navigate to: `your_instagram_activity/messages/`
   - Zip the entire `messages` folder
   - Upload the ZIP file

   **Option 2: Individual Files**
   - Navigate to: `your_instagram_activity/messages/inbox/[friend_name]/`
   - Select multiple `message_*.json` files
   - Upload them directly

3. **Upload and analyze:**
   - Open the web application
   - Enter your name as it appears in Instagram
   - Upload your files using either method
   - Wait for analysis to complete (much faster now!)

4. **Explore insights:**
   - View dashboard overview
   - Analyze individual friendships
   - Explore social network patterns
   - Compare messaging habits

## 🔧 Configuration

### Environment Variables
- `VITE_API_URL` - Backend API URL (default: http://localhost:5000)

### Customization
- Modify `tailwind.config.js` for custom styling
- Update `src/contexts/DataContext.jsx` for API endpoints
- Customize analysis logic in `backend/app.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔒 Privacy

- Your data is processed locally on the server
- No data is permanently stored
- All analysis is done in memory
- Files are cleaned up after processing

## 🆘 Support

If you encounter any issues:
1. Check the browser console for errors
2. Verify your Instagram data format
3. Ensure all dependencies are installed
4. Check the API endpoints are accessible

---

**Note:** This application requires Instagram data export in ZIP format. Make sure to follow Instagram's data download process to get the correct file format. 