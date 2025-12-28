import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Register.css";
import api from '../utils/api';

const Register = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [university, setUniversity] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    setAnimate(true);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/auth/register", {
        username: username,
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone_number: phoneNumber,
        password: password,
        university: university,
      });
      alert('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      if (error.response) {
        console.log("Registration error detail:", error.response.data);
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          alert(detail.map(err => `${err.loc[err.loc.length - 1]}: ${err.msg}`).join('\n'));
        } else {
          alert(typeof detail === 'string' ? detail : JSON.stringify(detail));
        }
      } else {
        alert("An error occurred during registration. Please try again.");
        console.error(error);
      }
    }
  };


  const handleLogIn = () => {
    navigate("/login");
  };

  return (
    <div className={`register-page ${animate ? "slide-in" : ""}`}>
      {/* LEFT SIDE - Colored Panel */}
      <div className="register-left">
        <Link to="/" className="register-logo">
          DZ-KITAB
        </Link>
        <div className="signin-content">
          <h2 className="signin-title">
            Already <span className="highlight">signed up ?</span>
          </h2>
          <p className="signin-subtitle">
            Log in to your account so you can continue exchanging books.
          </p>
          <button onClick={handleLogIn} className="signin-button">
            LOG IN
          </button>
        </div>
      </div>

      {/* RIGHT SIDE - Form Panel */}
      <div className="register-right">
        <div className="register-content">
          <h1 className="register-title">
            Create <span className="highlight">Your Account</span>
          </h1>
          <p className="register-subtitle">
            Let's get you all set up so you can start exchanging books.
          </p>

          <form onSubmit={handleSubmit} className="register-form">
            <div className="form-group">
              <input
                type="text"
                className="form-input"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <input
                  type="text"
                  className="form-input"
                  placeholder="First Name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Last Name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </div>
            </div>

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

            <div className="form-group">
              <input
                type="tel"
                className="form-input"
                placeholder="Phone Number (e.g. 0550123456)"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <select
                className="form-input form-select"
                value={university}
                onChange={(e) => setUniversity(e.target.value)}
                required
              >
                <option value="" disabled>
                  Select your university
                </option>
                <option value="ESTIN">ESTIN</option>
                <option value="USTHB">USTHB</option>
                <option value="ESI">ESI</option>
                <option value="EPAU">EPAU</option>
              </select>
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

            <button type="submit" className="register-button">
              SIGN UP
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
