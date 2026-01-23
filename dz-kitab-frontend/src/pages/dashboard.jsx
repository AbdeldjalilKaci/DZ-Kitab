import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from "recharts";
import Navbar from "../components/navbar";
import Footer from "../components/footer";
import "./dashboard.css";

// --- Données Mockées ---
const booksSoldData= [
  { month: "Jan", value: 1 }, { month: "Feb", value: 15 }, { month: "Mar", value: 0 }, { month: "Apr", value: 5 },
  { month: "May", value: 2 }, { month: "Jun", value: 13 }, { month: "Jul", value: 7 }, { month: "Aug", value: 7 },
  { month: "Sep", value: 4 }, { month: "Oct", value: 11 }, { month: "Nov", value: 8 }, { month: "Dec", value: 0 },
];
const miniChartData1 = [{ value: 12 }, { value: 15 }, { value: 10 }, { value: 18 }, { value: 14 }, { value: 17 }];
const miniChartData2 = [{ value: 8 }, { value: 6 }, { value: 10 }, { value: 7 }, { value: 9 }, { value: 10 }];
const miniChartData3 = [{ value: 45 }, { value: 52 }, { value: 48 }, { value: 58 }, { value: 50 }, { value: 55 }];

const topProperties = [
  { name: "Roselands", image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=80&h=80&fit=crop", percentage: 78 },
  { name: "Wayside", image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=80&h=80&fit=crop", percentage: 93 },
  { name: "Luminosa", image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=80&h=80&fit=crop", percentage: 78 },
  { name: "Good Residence", image: "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=80&h=80&fit=crop", percentage: 85 },
  { name: "Cyber Security Review", image: "https://images.unsplash.com/photo-1600607687644-aac4c3eac7f4?w=80&h=80&fit=crop", percentage: 84 },
  { name: "Antique Antiquites", image: "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=80&h=80&fit=crop", percentage: 84 },
];

// --- Composants ---
function MetricCard({ title, value, chart }) {
  return (
    <div className="metric-card">
      <div className="metric-card-title">{title}</div>
      <div className="metric-card-value">{value}</div>
      <div className="metric-card-chart">
        {chart ? chart : <div className="metric-card-chart-placeholder" />}
      </div>
    </div>
  );
}

function MiniLineChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorBlue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="value"
          stroke="#3B82F6"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorBlue)"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function PropertyItem({ name, image, percentage }) {
  return (
    <div className="property-item">
      <img src={image} alt={name} className="property-item-img" />
      <div className="property-item-content">
        <div className="property-item-name">{name}</div>
        <div className="property-item-progress-bg">
          <div
            className="property-item-progress-fill"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
      <div className="property-item-percentage">{percentage}%</div>
    </div>
  );
}

export default function Dashboard() {
  const [formData, setFormData] = useState({ firstName: "Jane", lastName: "Doe", email: "jane@example.com" });

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    console.log("Form submitted:", formData);
    alert("Profile updated successfully!");
  };

  return (
    <>
      <Navbar />

      <div className="dashboard-page">
        <div className="dashboard-container">

          {/* HEADER */}
          <div className="dashboard-header">
            <h1 className="dashboard-title">Dashboard</h1>
          </div>

          {/* --- BLOC DU HAUT --- */}
          <div className="dashboard-top-grid">
            {/* 6 Cartes à gauche */}
            <div className="metrics-grid">
              <MetricCard title="Total Listings" value={27} />
              <MetricCard title="Books Sold" value={15} />
              <MetricCard title="Purchase Requests" value={20} />
              <MetricCard title="Listings for Sale" value={17} chart={<MiniLineChart data={miniChartData1} />} />
              <MetricCard title="Listings for Exchange" value={10} chart={<MiniLineChart data={miniChartData2} />} />
              <MetricCard title="Received Messages" value={55} chart={<MiniLineChart data={miniChartData3} />} />
            </div>

            {/* Sales Overview à droite */}
            <div className="sales-overview-card">
              <h3 className="sales-overview-title">Sales Overview</h3>
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={booksSoldData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* ESPACE */}
          <div className="dashboard-spacer" />

          {/* --- BLOC DU BAS --- */}
          <div className="dashboard-bottom-grid">
            {/* Top Properties */}
            <div className="top-properties-card">
              <h3 className="top-properties-title">Most requested books</h3>
              <div className="top-properties-list">
                {topProperties.map((prop, i) => (
                  <PropertyItem key={i} {...prop} />
                ))}
              </div>
            </div>

            {/* Profile Settings */}
            <div className="profile-settings-card">
              {/* Header profil */}
             
              <div className="profile-header">
                <div className="profile-avatar-wrapper">
                  <img
                    src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=64&h=64&fit=crop"
                    className="profile-avatar"
                    alt="Profile"
                  />
                  <div className="profile-status-indicator"></div>
                </div>
                <div>
                  <h3 className="profile-title">Profile Settings</h3>
                  <p className="profile-subtitle">Manage your account information</p>
                </div>
              </div>
              
              
              {/* Formulaire */}
              <div className="profile-form-row">
                <div className="profile-form-group">
                  <label className="profile-form-label">First name</label>
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className="profile-form-input"
                  />
                </div>
                <div className="profile-form-group">
                  <label className="profile-form-label">Last name</label>
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    className="profile-form-input"
                  />
                </div>
              </div>

              <div className="profile-form-group-full">
                <label className="profile-form-label">Email address</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="profile-form-input"
                />
                
              </div>

              {/* Boutons */}
              <div className="profile-form-actions">
                <button className="profile-btn-cancel">Cancel</button>
                <button onClick={handleSubmit} className="profile-btn-submit">
                  Save Changes
                </button>
              </div>
              
            </div>
          </div>

        </div>
      </div>

      
    </>
  );
}