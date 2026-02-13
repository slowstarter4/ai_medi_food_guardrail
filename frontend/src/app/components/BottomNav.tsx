import { Home, User, ScanLine, Settings } from "lucide-react";
import { Link, useLocation } from "react-router";

export function BottomNav() {
  const location = useLocation();
  
  const navItems = [
    { path: "/", icon: Home, label: "홈" },
    { path: "/profile", icon: User, label: "프로필" },
    { path: "/scan", icon: ScanLine, label: "스캔" },
    { path: "/settings", icon: Settings, label: "설정" },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
      <div className="flex justify-around items-center h-16 max-w-2xl mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className="flex flex-col items-center justify-center flex-1 h-full"
            >
              <Icon
                className={`w-6 h-6 mb-1 ${
                  isActive ? "text-[#009688]" : "text-gray-500"
                }`}
              />
              <span
                className={`text-xs ${
                  isActive ? "text-[#009688] font-medium" : "text-gray-500"
                }`}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
