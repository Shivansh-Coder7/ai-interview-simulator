import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import CandidateDashboard from "./pages/CandidateDashboard";
import InterviewChat from "./pages/InterviewChat";
import Report from "./pages/Report";
import AdminDashboard from "./pages/AdminDashboard";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <CandidateDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/interview/:sessionId"
          element={
            <PrivateRoute>
              <InterviewChat />
            </PrivateRoute>
          }
        />
        <Route
          path="/report/:sessionId"
          element={
            <PrivateRoute>
              <Report />
            </PrivateRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <PrivateRoute>
              <AdminDashboard />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
