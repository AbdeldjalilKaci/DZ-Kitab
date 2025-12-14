import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    setAnimate(true);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Login submitted:", { email, password, rememberMe });
    // Add your login logic here
  };

  const handleSignUp = () => {
    navigate("/register");
  };

  return (
    <div className={`login-page ${animate ? "slide-in" : ""}`}>
      {/* LEFT SIDE */}
      <div className="login-left">
        <Link to="/" className="login-logo">
          DZ-KITAB
        </Link>

        <div className="login-content">
          <h1 className="login-title">
            Log in to <span className="highlight">Your Account</span>
          </h1>
          <p className="login-subtitle">
            Log in to your account so you can continue exchanging books.
          </p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <input
                type="email"
                className="form-input"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group password-group">
              <input
                type={showPassword ? "text" : "password"}
                className="form-input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label="Toggle password visibility"
              >
                {showPassword ? "👁️" : "👁️‍🗨️"}
              </button>
            </div>

            <div className="form-options">
              <label className="remember-me">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span>Remember Me</span>
              </label>
              <a href="#" className="forgot-password">
                Forgot Password
              </a>
            </div>

            <button type="submit" className="login-button">
              LOG IN
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT SIDE */}
      <div className="login-right">
        <div className="signup-content">
          <h2 className="signup-title">
            Don't Have an <span className="highlight">Account Yet ?</span>
          </h2>
          <p className="signup-subtitle">
            Let's get you all set up so you can start exchanging books.
          </p>
          <button onClick={handleSignUp} className="signup-button">
            SIGN UP
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
