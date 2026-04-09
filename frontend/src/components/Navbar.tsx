import { Link, useLocation } from "react-router-dom";
import { Moon, Sun, Menu, X, LogOut, Settings as SettingsIcon } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { axiosClient, apiUrl } from "@/lib/api";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const location = useLocation();
  const { user, login, logout } = useAuth();

  const handleGoogleSuccess = async (credentialResponse: any) => {
    if (credentialResponse.credential) {
      try {
        const res = await axiosClient.post(apiUrl("/api/v1/auth/google"), {
          id_token: credentialResponse.credential,
        });
        await login(res.data.access_token);
        toast.success("Đăng nhập thành công!");
      } catch (error) {
        console.error("Login failed", error);
        toast.error("Đăng nhập thất bại. Vui lòng thử lại.");
      }
    }
  };

  const handleLogout = () => {
    logout();
    toast.success("Đã đăng xuất");
  };

  const navItems = [
    { path: "/", label: "Trang chủ" },
    { path: "/cards", label: "Bộ bài" },
    { path: "/reading", label: "Xem bói" },
    { path: "/about", label: "Giới thiệu" },
  ];

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle("dark");
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-mystic-500 to-gold-500"></div>
            <span className="font-cinzel text-xl font-bold text-gradient">
              Black Luna Tarot
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`relative px-3 py-2 text-sm font-medium transition-colors hover:text-primary ${
                  location.pathname === item.path
                    ? "text-primary"
                    : "text-muted-foreground"
                }`}
              >
                {item.label}
                {location.pathname === item.path && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 rounded-md bg-primary/10"
                    initial={false}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
              </Link>
            ))}
          </div>

          {/* Theme Toggle & User/Login & Mobile Menu Button */}
          <div className="flex items-center space-x-4">
            
            <div className="hidden md:block">
              {user ? (
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium">Chào, {user.name}</span>
                  <Link to="/settings">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <SettingsIcon className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </Link>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleLogout}>
                    <LogOut className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ) : (
                <div className="scale-90 transform">
                  <GoogleLogin 
                    onSuccess={handleGoogleSuccess} 
                    onError={() => toast.error("Có lỗi xảy ra khi đăng nhập Google")}
                    useOneTap
                  />
                </div>
              )}
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="h-9 w-9"
            >
              {isDark ? (
                <Sun className="h-4 w-4 text-amber-500" />
              ) : (
                <Moon className="h-4 w-4 text-indigo-400" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? (
                <X className="h-4 w-4" />
              ) : (
                <Menu className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden"
          >
            <div className="space-y-1 pb-3 pt-2">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-3 py-2 text-base font-medium transition-colors hover:text-primary ${
                    location.pathname === item.path
                      ? "text-primary"
                      : "text-muted-foreground"
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  {item.label}
                </Link>
              ))}

              {/* Mobile Auth Menu */}
              <div className="mt-4 border-t pt-4 px-3 pb-2">
                {user ? (
                  <div className="space-y-3">
                    <div className="font-medium">Chào, {user.name}</div>
                    <Link to="/settings" className="flex items-center space-x-2 text-muted-foreground hover:text-primary" onClick={() => setIsOpen(false)}>
                      <SettingsIcon className="h-4 w-4" />
                      <span>Cài đặt Personalize</span>
                    </Link>
                    <button onClick={handleLogout} className="flex items-center space-x-2 text-destructive">
                      <LogOut className="h-4 w-4" />
                      <span>Đăng xuất</span>
                    </button>
                  </div>
                ) : (
                  <GoogleLogin 
                    onSuccess={handleGoogleSuccess} 
                    onError={() => toast.error("Có lỗi xảy ra khi đăng nhập Google")}
                  />
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
