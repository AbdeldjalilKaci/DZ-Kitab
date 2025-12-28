import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";
import api from '../utils/api';
import { useWishlist } from "../context/WishlistContext";
import { setCookie } from "../utils/cookies";

const Login = () => {
  const navigate = useNavigate();
  const { fetchWishlist } = useWishlist();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [animate, setAnimate] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setAnimate(true);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      });

      const { access_token, user } = response.data;
      setCookie('access_token', access_token, rememberMe ? 30 : 7);
      setCookie('user', JSON.stringify(user), rememberMe ? 30 : 7);


      // Refresh wishlist state
      fetchWishlist();

      alert('Login successful');

      navigate('/');
    } catch (error) {
      console.error("Login error:", error);
      const detail = error.response?.data?.detail || "An error occurred during login";
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail));
      alert(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
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
