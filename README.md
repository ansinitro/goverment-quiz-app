# 🎓 Government Service Exam Preparation - Kazakhstan

Interactive quiz application for preparing for the Government Service examination in the Republic of Kazakhstan.

## 🌟 Features

- **📚 Structured Learning**: Navigate through laws (zakons) and their sections (blocks)
- **🧠 Two Quiz Modes**: 
  - Practice all questions in order
  - Review your mistakes to improve weak areas
- **📊 Progress Tracking**: Automatic statistics tracking with accuracy percentage
- **✅ Instant Feedback**: Immediate answer validation with explanations
- **📱 Mobile-Friendly**: Responsive design works on all devices
- **💾 Persistent Data**: Progress saved locally in browser

## 🚀 Live Demo

**Web Version**: [https://YOUR_USERNAME.github.io/quiz-app/](https://YOUR_USERNAME.github.io/quiz-app/)

**Telegram Mini App**: [https://t.me/YOUR_BOT_NAME/quiz](https://t.me/YOUR_BOT_NAME/quiz)

## 📁 Project Structure

```
quiz-app/
├── index.html              # Main web version
├── telegram.html           # Telegram Mini App version
├── app.js                  # React application code
├── all_questions.json      # Questions database
└── README.md              # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Git installed on your computer
- GitHub account
- Web browser

### Step 1: Clone or Download
```bash
git clone https://github.com/YOUR_USERNAME/quiz-app.git
cd quiz-app
```

### Step 2: Add Your Questions
Place your `all_questions.json` file in the root directory.

### Step 3: Test Locally
Open `index.html` in your web browser to test locally.

### Step 4: Deploy to GitHub Pages
1. Push to GitHub
2. Go to repository Settings
3. Navigate to Pages section
4. Select branch `main` and folder `/ (root)`
5. Save and wait for deployment

## 📊 Questions JSON Format

Your `all_questions.json` should follow this structure:

```json
[
  {
    "theme_id": "1",
    "theme_name": "Конституция Республики Казахстан",
    "block_id": "1",
    "block_name": "Раздел I. Общие положения",
    "question_number": 1,
    "question": "Вопрос здесь?",
    "answers": {
      "1": "Первый вариант",
      "2": "Второй вариант",
      "3": "Третий вариант",
      "4": "Четвертый вариант"
    },
    "correct_answer": "1",
    "article": "Статья 15, пункт 2"
  }
]
```

## 🎮 How to Use

1. **Select Program**: Choose "Программа 2"
2. **Select Law**: Pick a law (zakon) to study
3. **Select Block**: Choose a specific section
4. **Choose Mode**: 
   - "Все вопросы" - Practice all questions
   - "Работа над ошибками" - Review mistakes
5. **Take Quiz**: Answer questions and get instant feedback
6. **Track Progress**: View your statistics and accuracy

## 🔧 Customization

### Change Colors
Edit `app.js` and modify Tailwind CSS classes:
- Primary color: `bg-indigo-600` → `bg-blue-600`
- Gradient: `from-blue-50 to-indigo-100` → your colors

### Add More Programs
Modify the `programs` object in `app.js`:
```javascript
const programs = { 
  'prog1': 'Программа 1',
  'prog2': 'Программа 2' 
};
```

## 📱 Telegram Mini App Setup

1. Create bot with @BotFather (`/newbot`)
2. Create mini app (`/newapp`)
3. Use URL: `https://YOUR_USERNAME.github.io/quiz-app/telegram.html`
4. Share the link: `https://t.me/YOUR_BOT_NAME/quiz`

## 🔄 Updating Questions

When you have new questions:

```bash
# Replace all_questions.json with new file
git add all_questions.json
git commit -m "Update questions database"
git push
```

Changes will appear on your website within a few minutes.

## 📈 Statistics Storage

- Statistics are stored in browser's localStorage
- Data persists between sessions
- Each block has independent statistics
- Clear browser data to reset statistics

## 🌐 Browser Support

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera
- ✅ Mobile browsers

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Created for preparing for Government Service examination in Kazakhstan.

## 📞 Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Ensure `all_questions.json` is in correct format
3. Verify GitHub Pages is enabled
4. Try clearing browser cache

## ⭐ Show Your Support

If this app helped you prepare for the exam, please give it a star on GitHub!

---

**Good luck with your exam preparation! 🎯**