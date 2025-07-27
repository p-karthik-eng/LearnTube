import mongoose from 'mongoose';

const AdminSchema = new mongoose.Schema({
  videoId:   { type: String, required: true, index: true },
  language:  { type: String, default: 'en' },
  url:       { type: String, required: true },
  title:     { type: String },
  duration:  { type: String },
  transcript:{ cleanText: String, chunks: Array },
  source:    { type: String, default: 'youtube-timedtext' },
  fetchedAt: { type: Date,   default: Date.now }
});

export default mongoose.models.AdminData
  || mongoose.model('AdminData', AdminSchema);
