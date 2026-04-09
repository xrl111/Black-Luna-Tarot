import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AnimatePresence } from "framer-motion";
import Navbar from "@/components/Navbar";
import Home from "@/pages/Home";
import TarotCards from "@/pages/TarotCards";
import CardDetail from "@/pages/CardDetail";
import Reading from "@/pages/Reading";
import About from "@/pages/About";
import FontShowcase from "@/components/FontShowcase";
import Settings from "@/pages/Settings";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "@/contexts/AuthContext";
import { Toaster } from "sonner";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "test-bypass-token";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-indigo-50 dark:from-slate-900 dark:via-purple-900 dark:to-indigo-900">
              <Navbar />
              <main className="container mx-auto px-4 py-8">
                <AnimatePresence mode="wait">
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/cards" element={<TarotCards />} />
                    <Route path="/cards/:id" element={<CardDetail />} />
                    <Route path="/reading" element={<Reading />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/fonts" element={<FontShowcase />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </AnimatePresence>
              </main>
              <Toaster position="top-center" richColors />
            </div>
          </Router>
        </AuthProvider>
      </QueryClientProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
