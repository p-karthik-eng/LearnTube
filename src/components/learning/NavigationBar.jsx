import ThemeToggle from "@/components/common/ThemeToggle";

export default function NavigationBar({ session, isDarkTheme, setIsDarkTheme, router }) {
  return (
    <nav className={`flex items-center justify-between px-8 py-4 border-b sticky top-0 z-50 transition-colors duration-300 ${
      isDarkTheme 
        ? 'bg-gray-800/80 backdrop-blur-sm border-gray-700 shadow-lg' 
        : 'bg-white border-gray-200 shadow-sm'
    }`}>
      <div className="flex items-center space-x-4">
        <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent select-none">
          LearnTube
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <div className={`hidden md:block text-sm ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>
          Welcome back, <span className={`font-medium ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
            {session?.user?.name || session?.user?.email}
          </span>
        </div>
        
        <ThemeToggle isDarkTheme={isDarkTheme} setIsDarkTheme={setIsDarkTheme} />

        <button
          className={`rounded-full border-2 p-1 hover:shadow-lg transition-all duration-200 hover:border-blue-400 ${
            isDarkTheme ? 'border-gray-600' : 'border-gray-300'
          }`}
          onClick={() => router.push("/profile")}
        >
          <img
            src={session?.user?.image || "/default-avatar.svg"}
            onError={e => { e.target.onerror = null; e.target.src = "/default-avatar.svg"; }}
            alt="Profile"
            className="w-10 h-10 rounded-full"
          />
        </button>
      </div>
    </nav>
  );
} 