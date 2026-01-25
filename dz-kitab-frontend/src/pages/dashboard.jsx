import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from "recharts";
import "./dashboard.css";
import api from "../utils/api";

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
      <img src={image || 'https://via.placeholder.com/64'} alt={name} className="property-item-img" />
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
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_listings: 0,
    books_sold: 0,
    purchase_requests: 0,
    listings_for_sale: 0,
    reserved_listings: 0,
    unread_messages: 0
  });
  const [salesData, setSalesData] = useState([]);
  const [popularListings, setPopularListings] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [profile, setProfile] = useState({ firstName: "", lastName: "", email: "" });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // 1. Overview Stats
        const overviewRes = await api.get('/api/dashboard/overview');
        setStats(overviewRes.data.stats);
        setProfile({
          firstName: overviewRes.data.user.username.split(" ")[0] || "User", // Fallback parsing
          lastName: overviewRes.data.user.username.split(" ")[1] || "",
          email: overviewRes.data.user.email
        });

        // 2. Sales Overview
        try {
          const salesRes = await api.get('/api/dashboard/sales-overview');
          if (salesRes.data?.data) {
            setSalesData(salesRes.data.data.map(d => ({ month: d.month, value: d.sales })));
          }
        } catch (e) {
          console.warn("Sales data fetch failed");
        }

        // 3. Popular Listings
        try {
          const popularRes = await api.get('/api/dashboard/popular-listings');
          setPopularListings(popularRes.data.listings.map(l => ({
            name: l.title,
            image: l.cover_image,
            percentage: l.percentage
          })));
        } catch (e) {
          console.warn("Popular listings fetch failed");
        }

        // 4. Recent Activity
        try {
          const activityRes = await api.get('/api/dashboard/recent-activity');
          setRecentActivity(activityRes.data.activities);
        } catch (e) {
          console.warn("Recent activity fetch failed");
        }

      } catch (error) {
        console.error("Dashboard loaded error:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleInputChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      await api.put('/api/dashboard/profile', {
        first_name: profile.firstName,
        last_name: profile.lastName,
        // Email usually distinct logical update, but keeping simple
      });
      alert("Profile updated successfully!");
    } catch (error) {
      console.error("Update failed", error);
      alert("Failed to update profile.");
    }
  };

  if (loading) return <div className="text-center p-10">Loading Dashboard...</div>;

  // Mock mini charts for visual filler (since backend doesn't provide historical trend array yet)
  const mockTrend = [{ value: 10 }, { value: 15 }, { value: 10 }, { value: 18 }, { value: 14 }, { value: 17 }];

  return (
    <>
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
              <MetricCard title="Total Listings" value={stats.total_listings} />
              <MetricCard title="Books Sold" value={stats.books_sold} />
              <MetricCard title="Purchase Requests" value={stats.purchase_requests} />
              <MetricCard title="Listings for Sale" value={stats.listings_for_sale} chart={<MiniLineChart data={mockTrend} />} />
              <MetricCard title="Reserved" value={stats.reserved_listings} chart={<MiniLineChart data={mockTrend} />} />
              <MetricCard title="Unread Messages" value={stats.unread_messages} chart={<MiniLineChart data={mockTrend} />} />
            </div>

            {/* Sales Overview à droite */}
            <div className="sales-overview-card">
              <h3 className="sales-overview-title">Sales Overview</h3>
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={salesData.length > 0 ? salesData : []}>
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
              <h3 className="top-properties-title">Most Viewed Listings</h3>
              <div className="top-properties-list">
                {popularListings.length > 0 ? popularListings.map((prop, i) => (
                  <PropertyItem key={i} {...prop} />
                )) : <p className="text-gray-500">No views yet.</p>}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="recent-activity-card" style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '20px' }}>Recent Activity</h3>
              <div className="activity-list">
                {recentActivity.length > 0 ? recentActivity.map((activity, i) => (
                  <div key={i} style={{ display: 'flex', gap: '12px', marginBottom: '16px', borderBottom: '1px solid #f3f4f6', paddingBottom: '12px' }}>
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '50%',
                      background: activity.type === 'notification' ? '#EBF5FF' : '#ECFDF5',
                      color: activity.type === 'notification' ? '#3B82F6' : '#10B981',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold'
                    }}>
                      {activity.type === 'notification' ? '🔔' : '⭐'}
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>{activity.title}</div>
                      <div style={{ fontSize: '13px', color: '#6B7280' }}>{activity.message}</div>
                      <div style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '4px' }}>
                        {new Date(activity.timestamp).toLocaleDateString()} {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                )) : <p className="text-gray-500">No recent activity.</p>}
              </div>
            </div>

            {/* Profile Settings */}
            <div className="profile-settings-card">
              {/* Header profil */}

              <div className="profile-header">
                <div className="profile-avatar-wrapper">
                  <div className="profile-avatar" style={{ backgroundColor: '#ccc', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>
                    {profile.firstName ? profile.firstName[0].toUpperCase() : 'U'}
                  </div>
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
                    value={profile.firstName}
                    onChange={handleInputChange}
                    className="profile-form-input"
                  />
                </div>
                <div className="profile-form-group">
                  <label className="profile-form-label">Last name</label>
                  <input
                    type="text"
                    name="lastName"
                    value={profile.lastName}
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
                  value={profile.email}
                  readOnly
                  className="profile-form-input bg-gray-100"
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