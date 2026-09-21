import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./Login";
import Register from "./Register";
import Protected from "./Protected";
import Dashboard from "./Dashboard";
import AuthLogs from "./AuthLogs";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/protected"
          element={<Protected />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route 
        path="/auth-logs" 
        element={<AuthLogs />} 
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;