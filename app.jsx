const { useState, useEffect } = React;

// Lucide icons as React components
const createIcon = (iconName) => {
  return (props) => {
    const { className = "w-6 h-6", ...rest } = props;
    return React.createElement('i', {
      'data-lucide': iconName,
      className,
      ...rest
    });
  };
};

const BookOpen = createIcon('book-open');
const Award = createIcon('award');
const RotateCcw = createIcon('rotate-ccw');
const CheckCircle = createIcon('check-circle');
const XCircle = createIcon('x-circle');
const ChevronRight = createIcon('chevron-right');
const Menu = createIcon('menu');
const Target = createIcon('target');
const Brain = createIcon('brain');
const TrendingUp = createIcon('trending-up');

const QuizApp = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [selectedZakon, setSelectedZakon] = useState(null);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [quizMode, setQuizMode] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [userAnswers, setUserAnswers] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [stats, setStats] = useState({});

  useEffect(() => {
    loadQuestions();
    loadStats();
  }, []);

  useEffect(() => {
    // Initialize Lucide icons after render
    if (window.lucide) {
      window.lucide.createIcons();
    }
  });

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const response = await fetch('./all_questions.json');
      if (!response.ok) {
        throw new Error('Failed to load questions');
      }
      const data = await response.json();
      
      const processedData = data.map(q => ({
        ...q,
        block_id: q.block_id || '0',
        block_name: q.block_name || 'Основной блок'
      }));
      
      setQuestions(processedData);
      setLoading(false);
    } catch (err) {
      console.error('Error loading questions:', err);
      setError('Не удалось загрузить вопросы. Убедитесь, что файл all_questions.json находится в корневой папке.');
      setLoading(false);
    }
  };

  const loadStats = () => {
    try {
      const savedStats = localStorage.getItem('quizStats');
      if (savedStats) {
        setStats(JSON.parse(savedStats));
      }
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const saveStats = (newStats) => {
    try {
      localStorage.setItem('quizStats', JSON.stringify(newStats));
      setStats(newStats);
    } catch (err) {
      console.error('Error saving stats:', err);
    }
  };

  const getStructuredData = () => {
    const programs = { 'prog2': 'Программа 2' };
    const structure = {};

    questions.forEach(q => {
      const prog = 'prog2';
      if (!structure[prog]) structure[prog] = {};
      if (!structure[prog][q.theme_id]) {
        structure[prog][q.theme_id] = {
          name: q.theme_name,
          blocks: {}
        };
      }
      const blockId = q.block_id || '0';
      if (!structure[prog][q.theme_id].blocks[blockId]) {
        structure[prog][q.theme_id].blocks[blockId] = {
          name: q.block_name || 'Основной блок',
          questions: []
        };
      }
      structure[prog][q.theme_id].blocks[blockId].questions.push(q);
    });

    return { programs, structure };
  };

  const { programs, structure } = getStructuredData();

  const getFilteredQuestions = () => {
    if (!selectedProgram || !selectedZakon || !selectedBlock) return [];
    const questions = structure[selectedProgram][selectedZakon].blocks[selectedBlock].questions;
    
    if (quizMode === 'mistakes') {
      const key = `${selectedProgram}_${selectedZakon}_${selectedBlock}`;
      const blockStats = stats[key];
      if (blockStats && blockStats.incorrectQuestions) {
        return questions.filter((_, idx) => blockStats.incorrectQuestions.includes(idx));
      }
    }
    
    return questions;
  };

  const startQuiz = (mode) => {
    setQuizMode(mode);
    setCurrentQuestionIndex(0);
    setUserAnswers([]);
    setShowResults(false);
    setSelectedAnswer(null);
    setShowExplanation(false);
  };

  const handleAnswerSelect = (answerId) => {
    if (showExplanation) return;
    setSelectedAnswer(answerId);
  };

  const handleSubmitAnswer = () => {
    const filteredQuestions = getFilteredQuestions();
    const currentQuestion = filteredQuestions[currentQuestionIndex];
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;

    setUserAnswers([...userAnswers, {
      questionId: currentQuestionIndex,
      selectedAnswer,
      isCorrect
    }]);

    setShowExplanation(true);

    const key = `${selectedProgram}_${selectedZakon}_${selectedBlock}`;
    const newStats = { ...stats };
    if (!newStats[key]) {
      newStats[key] = { correct: 0, total: 0, incorrectQuestions: [] };
    }
    newStats[key].total += 1;
    if (isCorrect) {
      newStats[key].correct += 1;
      newStats[key].incorrectQuestions = newStats[key].incorrectQuestions.filter(
        idx => idx !== currentQuestionIndex
      );
    } else {
      if (!newStats[key].incorrectQuestions.includes(currentQuestionIndex)) {
        newStats[key].incorrectQuestions.push(currentQuestionIndex);
      }
    }
    saveStats(newStats);
  };

  const handleNextQuestion = () => {
    const filteredQuestions = getFilteredQuestions();
    if (currentQuestionIndex < filteredQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      setShowResults(true);
    }
  };

  const resetQuiz = () => {
    setSelectedProgram(null);
    setSelectedZakon(null);
    setSelectedBlock(null);
    setQuizMode(null);
    setCurrentQuestionIndex(0);
    setUserAnswers([]);
    setShowResults(false);
  };

  const getStatsForCurrentSelection = () => {
    const key = `${selectedProgram}_${selectedZakon}_${selectedBlock}`;
    return stats[key] || { correct: 0, total: 0, incorrectQuestions: [] };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Загрузка вопросов...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md text-center">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Ошибка загрузки</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md text-center">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Нет вопросов</h2>
          <p className="text-gray-600">База вопросов пуста. Пожалуйста, добавьте файл all_questions.json.</p>
        </div>
      </div>
    );
  }

  if (!selectedProgram) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <div className="flex items-center gap-3 mb-6">
              <BookOpen className="w-10 h-10 text-indigo-600" />
              <h1 className="text-3xl font-bold text-gray-800">Подготовка к экзамену</h1>
            </div>
            <p className="text-gray-600 mb-4">Выберите программу для начала подготовки</p>
            <p className="text-sm text-gray-500 mb-8">Всего вопросов в базе: {questions.length}</p>
            
            {Object.entries(programs).map(([progId, progName]) => (
              <button
                key={progId}
                onClick={() => setSelectedProgram(progId)}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl p-6 mb-4 hover:from-indigo-600 hover:to-purple-700 transition-all transform hover:scale-105 flex items-center justify-between"
              >
                <span className="text-xl font-semibold">{progName}</span>
                <ChevronRight className="w-6 h-6" />
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!selectedZakon && selectedProgram) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <button onClick={resetQuiz} className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center gap-2">
            <ChevronRight className="w-5 h-5 rotate-180" />
            Назад
          </button>
          
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Выберите закон</h2>
            
            <div className="space-y-4">
              {Object.entries(structure[selectedProgram]).map(([zakonId, zakonData]) => {
                const totalQuestions = Object.values(zakonData.blocks).reduce(
                  (sum, block) => sum + block.questions.length, 0
                );
                
                return (
                  <button
                    key={zakonId}
                    onClick={() => setSelectedZakon(zakonId)}
                    className="w-full bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-indigo-500 hover:shadow-lg transition-all text-left"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-2">{zakonData.name}</h3>
                        <p className="text-sm text-gray-500">
                          {Object.keys(zakonData.blocks).length} разделов • {totalQuestions} вопросов
                        </p>
                      </div>
                      <ChevronRight className="w-6 h-6 text-gray-400 mt-1" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!selectedBlock && selectedZakon) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <button onClick={() => setSelectedZakon(null)} className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center gap-2">
            <ChevronRight className="w-5 h-5 rotate-180" />
            Назад
          </button>
          
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">{structure[selectedProgram][selectedZakon].name}</h2>
            <p className="text-gray-600 mb-6">Выберите раздел для изучения</p>
            
            <div className="space-y-4">
              {Object.entries(structure[selectedProgram][selectedZakon].blocks).map(([blockId, blockData]) => {
                const key = `${selectedProgram}_${selectedZakon}_${blockId}`;
                const blockStats = stats[key] || { correct: 0, total: 0 };
                const accuracy = blockStats.total > 0 ? Math.round((blockStats.correct / blockStats.total) * 100) : 0;
                
                return (
                  <button
                    key={blockId}
                    onClick={() => setSelectedBlock(blockId)}
                    className="w-full bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-indigo-500 hover:shadow-lg transition-all text-left"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-800 mb-2">{blockData.name}</h3>
                        <p className="text-sm text-gray-500">{blockData.questions.length} вопросов</p>
                      </div>
                      <ChevronRight className="w-6 h-6 text-gray-400 mt-1" />
                    </div>
                    
                    {blockStats.total > 0 && (
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1">
                          <Target className="w-4 h-4 text-green-500" />
                          <span className="text-gray-600">Точность: <strong>{accuracy}%</strong></span>
                        </div>
                        <div className="text-gray-500">
                          Пройдено: {blockStats.total}
                        </div>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!quizMode) {
    const currentStats = getStatsForCurrentSelection();
    const accuracy = currentStats.total > 0 ? Math.round((currentStats.correct / currentStats.total) * 100) : 0;
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <button onClick={() => setSelectedBlock(null)} className="mb-4 text-indigo-600 hover:text-indigo-800 flex items-center gap-2">
            <ChevronRight className="w-5 h-5 rotate-180" />
            Назад
          </button>
          
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              {structure[selectedProgram][selectedZakon].blocks[selectedBlock].name}
            </h2>
            <p className="text-gray-600 mb-6">
              {structure[selectedProgram][selectedZakon].blocks[selectedBlock].questions.length} вопросов
            </p>
            
            {currentStats.total > 0 && (
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Ваша статистика</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-indigo-600">{currentStats.total}</div>
                    <div className="text-sm text-gray-600">Всего</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{currentStats.correct}</div>
                    <div className="text-sm text-gray-600">Верных</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">{accuracy}%</div>
                    <div className="text-sm text-gray-600">Точность</div>
                  </div>
                </div>
              </div>
            )}

            <h3 className="text-lg font-semibold text-gray-800 mb-4">Выберите режим</h3>
            
            <div className="space-y-4">
              <button
                onClick={() => startQuiz('all')}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl p-6 hover:from-indigo-600 hover:to-purple-700 transition-all"
              >
                <div className="flex items-center gap-4">
                  <Brain className="w-8 h-8" />
                  <div className="text-left">
                    <div className="text-xl font-semibold">Все вопросы</div>
                    <div className="text-sm opacity-90">Пройти все вопросы по порядку</div>
                  </div>
                </div>
              </button>

              {currentStats.incorrectQuestions && currentStats.incorrectQuestions.length > 0 && (
                <button
                  onClick={() => startQuiz('mistakes')}
                  className="w-full bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-xl p-6 hover:from-red-600 hover:to-orange-700 transition-all"
                >
                  <div className="flex items-center gap-4">
                    <TrendingUp className="w-8 h-8" />
                    <div className="text-left">
                      <div className="text-xl font-semibold">Работа над ошибками</div>
                      <div className="text-sm opacity-90">
                        {currentStats.incorrectQuestions.length} вопросов, в которых были ошибки
                      </div>
                    </div>
                  </div>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (showResults) {
    const correctCount = userAnswers.filter(a => a.isCorrect).length;
    const totalCount = userAnswers.length;
    const percentage = Math.round((correctCount / totalCount) * 100);
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <Award className="w-20 h-20 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Тест завершен!</h2>
            
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-8 mb-8">
              <div className="text-6xl font-bold text-indigo-600 mb-2">{percentage}%</div>
              <div className="text-xl text-gray-600 mb-4">
                {correctCount} из {totalCount} правильных ответов
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-green-500 to-blue-500 h-full transition-all duration-1000"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>

            <div className="flex gap-4 justify-center flex-wrap">
              <button
                onClick={() => startQuiz(quizMode)}
                className="px-8 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all flex items-center gap-2"
              >
                <RotateCcw className="w-5 h-5" />
                Пройти снова
              </button>
              <button
                onClick={resetQuiz}
                className="px-8 py-3 bg-gray-600 text-white rounded-xl hover:bg-gray-700 transition-all"
              >
                Главное меню
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const filteredQuestions = getFilteredQuestions();
  const currentQuestion = filteredQuestions[currentQuestionIndex];
  
  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Вопрос не найден</p>
          <button onClick={resetQuiz} className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg">
            Вернуться
          </button>
        </div>
      </div>
    );
  }
  
  const isCorrect = selectedAnswer === currentQuestion.correct_answer;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="text-sm text-gray-500">
              Вопрос {currentQuestionIndex + 1} из {filteredQuestions.length}
            </div>
            <button onClick={resetQuiz} className="text-gray-500 hover:text-gray-700">
              <Menu className="w-6 h-6" />
            </button>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2 mb-8">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentQuestionIndex + 1) / filteredQuestions.length) * 100}%` }}
            />
          </div>

          <h3 className="text-2xl font-bold text-gray-800 mb-8">{currentQuestion.question}</h3>

          <div className="space-y-4 mb-8">
            {Object.entries(currentQuestion.answers).map(([answerId, answerText]) => {
              let buttonClass = "w-full p-6 rounded-xl border-2 transition-all text-left ";
              
              if (!showExplanation) {
                buttonClass += selectedAnswer === answerId
                  ? "border-indigo-500 bg-indigo-50"
                  : "border-gray-200 hover:border-indigo-300 bg-white";
              } else {
                if (answerId === currentQuestion.correct_answer) {
                  buttonClass += "border-green-500 bg-green-50";
                } else if (answerId === selectedAnswer) {
                  buttonClass += "border-red-500 bg-red-50";
                } else {
                  buttonClass += "border-gray-200 bg-gray-50 opacity-50";
                }
              }

              return (
                <button
                  key={answerId}
                  onClick={() => handleAnswerSelect(answerId)}
                  disabled={showExplanation}
                  className={buttonClass}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-lg">{answerText}</span>
                    {showExplanation && answerId === currentQuestion.correct_answer && (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    )}
                    {showExplanation && answerId === selectedAnswer && answerId !== currentQuestion.correct_answer && (
                      <XCircle className="w-6 h-6 text-red-600" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {showExplanation && (
            <div className={`p-6 rounded-xl mb-6 ${isCorrect ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'}`}>
              <div className="flex items-center gap-2 mb-2">
                {isCorrect ? (
                  <>
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <span className="font-semibold text-green-800">Правильно!</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-6 h-6 text-red-600" />
                    <span className="font-semibold text-red-800">Неправильно</span>
                  </>
                )}
              </div>
              {currentQuestion.article && (
                <p className="text-sm text-gray-700">
                  <strong>Основание:</strong> {currentQuestion.article}
                </p>
              )}
            </div>
          )}

          <div className="flex gap-4">
            {!showExplanation ? (
              <button
                onClick={handleSubmitAnswer}
                disabled={!selectedAnswer}
                className={`flex-1 py-4 rounded-xl font-semibold transition-all ${
                  selectedAnswer
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
              >
                Ответить
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="flex-1 py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all flex items-center justify-center gap-2"
              >
                {currentQuestionIndex < filteredQuestions.length - 1 ? (
                  <>
                    Следующий вопрос
                    <ChevronRight className="w-5 h-5" />
                  </>
                ) : (
                  'Показать результаты'
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<QuizApp />);