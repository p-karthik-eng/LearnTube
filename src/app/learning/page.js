"use client";
import { useSession } from "next-auth/react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import NavigationBar from "@/components/learning/NavigationBar";
import LessonContent from "@/components/learning/LessonContent";
import CourseSidebar from "@/components/learning/CourseSidebar";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ErrorDisplay from "@/components/common/ErrorDisplay";

export default function LearningPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [lessonType, setLessonType] = useState("video");
  const [showQuiz, setShowQuiz] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(false);
  const [courseData, setCourseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [selectedLessonId, setSelectedLessonId] = useState(null);

  // Get course URL from search params
  const courseUrl = searchParams.get('url');

  // Fetch course data from backend
  useEffect(() => {
    const fetchCourseData = async () => {
      setLoading(true);
      setTimeout(() => {
        const data = getDummyCourseData();
        setCourseData(data);
        setSelectedLessonId(data.lessons.find(lesson => lesson.current)?.id || data.lessons[0]?.id);
        setLoading(false);
      }, 500);
    };
    fetchCourseData();
  }, [courseUrl]);

  useEffect(() => {
    if (courseData && courseData.lessons) {
      setLessons(courseData.lessons);
    }
  }, [courseData]);

  const calculateProgress = () => {
    if (!lessons.length) return "0/0";
    const completedCount = lessons.filter(lesson => lesson.completed).length;
    return `${completedCount}/${lessons.length}`;
  };

  const selectedLesson = courseData?.lessons?.find(lesson => lesson.id === selectedLessonId);

  // --- DUMMY DATA (matches user JSON) ---
  const getDummyCourseData = () => ({
    courseInfo: {
      title: "JavaScript Programming Essentials",
      subtitle: "Master the basics of JavaScript step-by-step",
      duration: "1h 30min",
      totalLessons: 3
    },
    videoSource: {
      url: "https://www.youtube.com/watch?v=W6NZfCO5SIk"
    },
    courseOverview: {
      title: "JavaScript Programming Essentials",
      duration: "1h 30min",
      description: "A beginner-friendly course to master JavaScript fundamentals.",
      learningObjectives: [
        "Understand what JavaScript is and where it runs",
        "Learn about variables, data types, and functions",
        "Write and invoke your own JavaScript functions"
      ],
      targetAudience: [
        "Beginners to programming",
        "Web development students",
        "Anyone new to JavaScript"
      ],
      potentialCareers: [
        { title: "Frontend Developer", salary: "$60,000 - $120,000", avg: "$85,000" }
      ]
    },
    lessons: [
      {
        id: 1,
        title: "Introduction to JavaScript",
        subtitle: "Understanding what JavaScript is and why it's important",
        type: "video",
        videoMeta: {
          start: "00:00:00",
          end: "00:05:30"
        },
        completed: false,
        current: true,
        content: {
          introduction: "In this lesson, you'll learn the basics of what JavaScript is and where it runs.",
          sections: [
            {
              title: "What is JavaScript?",
              type: "concept",
              points: [
                {
                  subtitle: "Definition",
                  content: "JavaScript is a programming language used to make web pages interactive."
                },
                {
                  subtitle: "Where does it run?",
                  content: "JavaScript runs in the browser and on the server using Node.js."
                }
              ]
            }
          ],
          conclusion: "JavaScript is essential for interactive web development."
        },
        quizzes: [
          {
            id: 1,
            question: "What is the primary purpose of JavaScript?",
            type: "multiple_choice",
            options: ["Styling websites", "Creating web servers", "Making web pages interactive", "Managing databases"],
            correctAnswer: 2,
            answer: "Making web pages interactive",
            explanation: "JavaScript allows you to add interactivity like click events, animations, etc."
          }
        ]
      },
      {
        id: 2,
        title: "Variables and Data Types",
        subtitle: "Learn about let, const, and basic data types in JS",
        type: "video",
        videoMeta: {
          start: "00:05:31",
          end: "00:17:45"
        },
        completed: false,
        current: false,
        content: {
          introduction: "This lesson introduces variables in JavaScript and how data is stored.",
          sections: [
            {
              title: "Declaring Variables",
              type: "concept",
              points: [
                {
                  subtitle: "let and const",
                  content: "`let` allows reassignment, `const` does not."
                }
              ]
            },
            {
              title: "Data Types",
              type: "concept",
              points: [
                {
                  subtitle: "Primitive types",
                  content: "Includes string, number, boolean, null, undefined, symbol."
                }
              ]
            }
          ],
          conclusion: "Variables hold values and are the foundation of logic in JavaScript."
        },
        quizzes: [
          {
            id: 1,
            question: "Which keyword prevents variable reassignment?",
            type: "multiple_choice",
            options: ["let", "var", "const", "define"],
            correctAnswer: 2,
            answer: "const",
            explanation: "`const` creates a read-only reference to a value."
          }
        ]
      },
      {
        id: 3,
        title: "Functions in JavaScript",
        subtitle: "Defining and invoking functions",
        type: "video",
        videoMeta: {
          start: "00:17:46",
          end: "00:28:00"
        },
        completed: false,
        current: false,
        content: {
          introduction: "This lesson explores functions and their importance.",
          sections: [
            {
              title: "Function Basics",
              type: "concept",
              points: [
                {
                  subtitle: "Function declaration",
                  content: "Use the `function` keyword to define a function."
                },
                {
                  subtitle: "Calling a function",
                  content: "Use parentheses after the function name to invoke it."
                }
              ]
            },
            {
              title: "Function Parameters",
              type: "advanced",
              points: [
                {
                  subtitle: "Arguments",
                  content: "Functions can accept inputs called parameters or arguments."
                }
              ]
            }
          ],
          conclusion: "Functions allow you to write reusable blocks of code."
        },
        quizzes: [
          {
            id: 1,
            question: "What does a function return if no return statement is present?",
            type: "multiple_choice",
            options: ["0", "null", "undefined", "false"],
            correctAnswer: 2,
            answer: "undefined",
            explanation: "By default, functions return `undefined` if no return value is specified."
          }
        ]
      }
    ]
  });

  if (loading) {
    return <LoadingSpinner isDarkTheme={isDarkTheme} />;
  }

  if (error && !courseData) {
    return <ErrorDisplay error={error} isDarkTheme={isDarkTheme} />;
  }

  if (!courseData) {
    return (
      <div className={`font-inter transition-colors duration-300 ${isDarkTheme ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="text-gray-500 text-6xl mb-4">📚</div>
            <h2 className={`text-2xl font-bold mb-2 ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>No Course Data</h2>
            <p className={`${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Please provide a valid course URL</p>
          </div>
        </div>
      </div>
    );
  }

  const { courseInfo, videoSource } = courseData;
  const currentProgress = calculateProgress();

  return (
    <div className={`font-inter transition-colors duration-300 ${isDarkTheme ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <NavigationBar 
        session={session} 
        isDarkTheme={isDarkTheme} 
        setIsDarkTheme={setIsDarkTheme}
        router={router}
      />
      <div className="flex">
        <LessonContent 
          courseInfo={courseInfo}
          selectedLesson={selectedLesson}
          currentProgress={currentProgress}
          lessonType={lessonType}
          setLessonType={setLessonType}
          showQuiz={showQuiz}
          setShowQuiz={setShowQuiz}
          isDarkTheme={isDarkTheme}
          videoSource={videoSource}
        />
        <CourseSidebar 
          courseOverview={courseData.courseOverview}
          lessons={lessons}
          setLessons={setLessons}
          selectedLessonId={selectedLessonId}
          setSelectedLessonId={setSelectedLessonId}
          isDarkTheme={isDarkTheme}
        />
      </div>
    </div>
  );
} 
