import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from "recharts";
import { Camera } from "lucide-react";
import NavAdmin from "./navbarAdmin";

function MetricCard({ title, value, chart }) {
  return (
    <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>{title}</div>
      <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>{value}</div>
      {chart && <div style={{ height: '60px' }}>{chart}</div>}
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
        <Area type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} fill="url(#colorBlue)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function BookItem({ title, category, listings, image, percentage }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 0', borderBottom: '1px solid #F3F4F6' }}>
      <img src={image} alt={title} style={{ width: '60px', height: '60px', borderRadius: '8px', objectFit: 'cover' }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>{title}</div>
        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '8px' }}>{category} • {listings} listings</div>
        <div style={{ width: '100%', height: '6px', background: '#E5E7EB', borderRadius: '3px' }}>
          <div style={{ width: `${percentage}%`, height: '100%', background: '#3B82F6', borderRadius: '3px', transition: 'width 0.3s' }} />
        </div>
      </div>
      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827' }}>{percentage}%</div>
    </div>
  );
}

function CategoryItem({ name, value, color, percentage }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 0', borderBottom: '1px solid #F3F4F6' }}>
      <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: color, flexShrink: 0 }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>{name}</div>
        <div style={{ fontSize: '12px', color: '#6B7280' }}>{value} sold listings</div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>{percentage}%</div>
        <div style={{ fontSize: '11px', color: '#6B7280' }}>{value}</div>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState({});
  const [newListings, setNewListings] = useState([]);
  const [topBooks, setTopBooks] = useState([]);
  const [salesByCategory, setSalesByCategory] = useState([]);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: ""
  });
  const [profileImage, setProfileImage] = useState("https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const API_URL = "http://localhost:8000";

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No admin token found');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Fetch admin dashboard stats
      const statsRes = await fetch(`${API_URL}/api/admin/stats/dashboard`, { headers });
      const stats = await statsRes.json();

      // Transform metrics data
      setMetrics({
        totalUsers: stats.users?.total || 0,
        totalListings: stats.announcements?.total || 0,
        activeListings: stats.announcements?.active || 0,
        activeUsers30d: stats.users?.active || 0,
        newListings30d: stats.announcements?.new_this_week || 0,
        activeUsersTrend: [
          { value: stats.users?.total - 339 || 1050 },
          { value: stats.users?.total - 269 || 1120 },
          { value: stats.users?.total - 209 || 1180 },
          { value: stats.users?.total - 142 || 1247 },
          { value: stats.users?.total - 79 || 1310 },
          { value: stats.users?.total || 1389 }
        ],
        newListingsTrend: [
          { value: stats.announcements?.total - 565 || 3456 },
          { value: stats.announcements?.total - 423 || 3598 },
          { value: stats.announcements?.total - 309 || 3712 },
          { value: stats.announcements?.total - 176 || 3845 },
          { value: stats.announcements?.total - 129 || 3892 },
          { value: stats.announcements?.total || 4021 }
        ]
      });

      // Fetch popular books
      const popularRes = await fetch(`${API_URL}/api/admin/stats/popular-books?limit=6`, { headers });
      const popular = await popularRes.json();

      const booksData = popular.books?.map((book, index) => ({
        title: book.title,
        category: book.categories || "General",
        listings: book.total_announcements,
        image: book.cover_image_url || "https://images.unsplash.com/photo-1589998059171-988d887df646?w=80&h=80&fit=crop",
        percentage: Math.min(100, Math.floor((book.total_announcements / (popular.books[0]?.total_announcements || 1)) * 100))
      })) || [];
      setTopBooks(booksData);

      // Fetch sales by category
      const categoryRes = await fetch(`${API_URL}/api/admin/stats/sales-by-category`, { headers });
      const categoryData = await categoryRes.json();

      const colors = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"];
      const categoriesData = categoryData.categories?.map((cat, index) => ({
        name: cat.category,
        value: cat.total_sold,
        color: colors[index % colors.length],
        percentage: cat.percentage
      })) || [];
      setSalesByCategory(categoriesData);

      // Generate new listings chart data (mock for now, can be added to backend)
      const monthlyData = [
        { month: "Jan", value: 234 }, { month: "Feb", value: 267 }, { month: "Mar", value: 298 },
        { month: "Apr", value: 312 }, { month: "May", value: 345 }, { month: "Jun", value: 378 },
        { month: "Jul", value: 402 }, { month: "Aug", value: 389 }, { month: "Sep", value: 421 },
        { month: "Oct", value: 445 }, { month: "Nov", value: 467 }, { month: "Dec", value: stats.announcements?.new_this_week || 489 }
      ];
      setNewListings(monthlyData);

      // Fetch admin profile
      const profileRes = await fetch(`${API_URL}/auth/me`, { headers });
      const profile = await profileRes.json();
      setFormData({
        firstName: profile.first_name || "Admin",
        lastName: profile.last_name || "User",
        email: profile.email || ""
      });

    } catch (error) {
      console.error('Error fetching admin data:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setMessage({ type: "", text: "" });

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/dashboard/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          first_name: formData.firstName,
          last_name: formData.lastName
        })
      });

      if (response.ok) {
        setMessage({ 
          type: "success", 
          text: "Profile updated successfully!" 
        });
      } else {
        throw new Error('Update failed');
      }
    } catch (error) {
      setMessage({ 
        type: "error", 
        text: "Failed to update profile. Please try again." 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    fetchAdminData();
    setMessage({ type: "", text: "" });
  };

  const totalSales = salesByCategory.reduce((sum, cat) => sum + cat.value, 0);

  return (
    <>
      <NavAdmin />
      <div style={{ minHeight: '100vh', background: '#F9FAFB', padding: '20px' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          {/* HEADER */}
          <div style={{ marginBottom: '32px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Admin Dashboard</h1>
            <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '4px' }}>Welcome to DZ-Kitab</p>
          </div>

          {/* METRICS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '20px', marginBottom: '32px' }}>
            <MetricCard title="Total Users" value={metrics.totalUsers} />
            <MetricCard title="Total Listings" value={metrics.totalListings} />
            <MetricCard title="Active Listings" value={metrics.activeListings} />
            <MetricCard title="Active Users (30d)" value={metrics.activeUsers30d} chart={<MiniLineChart data={metrics.activeUsersTrend} />} />
            <MetricCard title="New Listings (30d)" value={metrics.newListings30d} chart={<MiniLineChart data={metrics.newListingsTrend} />} />
          </div>

          {/* PROFILE SETTINGS */}
          <div style={{ background: 'white', borderRadius: '12px', padding: '32px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '32px' }}>
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Profile Settings</h3>
              <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '4px' }}>Manage your account information</p>
            </div>

            <div style={{ display: 'flex', gap: '32px' }}>
              {/* Profile Image */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                <div style={{ position: 'relative', width: '160px', height: '160px' }}>
                  <img 
                    src={profileImage} 
                    alt="Admin profile" 
                    style={{ 
                      width: '100%', 
                      height: '100%', 
                      borderRadius: '50%', 
                      objectFit: 'cover',
                      border: '4px solid #E5E7EB'
                    }} 
                  />
                  <label 
                    htmlFor="profile-upload"
                    style={{
                      position: 'absolute',
                      bottom: '8px',
                      right: '8px',
                      width: '40px',
                      height: '40px',
                      background: '#3B82F6',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      border: '3px solid white',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#2563EB'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#3B82F6'}
                  >
                    <Camera size={20} color="white" />
                  </label>
                  <input
                    id="profile-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                  />
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                    {formData.firstName} {formData.lastName}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>Administrator</div>
                </div>
              </div>

              {/* Form Fields */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                  {/* First Name */}
                  <div>
                    <label 
                      htmlFor="firstName" 
                      style={{ 
                        display: 'block', 
                        fontSize: '14px', 
                        fontWeight: '600', 
                        color: '#374151', 
                        marginBottom: '8px' 
                      }}
                    >
                      First Name
                    </label>
                    <input
                      type="text"
                      id="firstName"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      required
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        fontSize: '14px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        outline: 'none',
                        transition: 'all 0.2s',
                        boxSizing: 'border-box'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                      onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
                    />
                  </div>

                  {/* Last Name */}
                  <div>
                    <label 
                      htmlFor="lastName" 
                      style={{ 
                        display: 'block', 
                        fontSize: '14px', 
                        fontWeight: '600', 
                        color: '#374151', 
                        marginBottom: '8px' 
                      }}
                    >
                      Last Name
                    </label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      required
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        fontSize: '14px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        outline: 'none',
                        transition: 'all 0.2s',
                        boxSizing: 'border-box'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                      onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
                    />
                  </div>
                </div>

                {/* Email Address */}
                <div style={{ marginBottom: '20px' }}>
                  <label 
                    htmlFor="email" 
                    style={{ 
                      display: 'block', 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      color: '#374151', 
                      marginBottom: '8px' 
                    }}
                  >
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    readOnly
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      fontSize: '14px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '8px',
                      outline: 'none',
                      transition: 'all 0.2s',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                    onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
                  />
                </div>

                {/* Message Display */}
                {message.text && (
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    marginBottom: '20px',
                    background: message.type === 'success' ? '#D1FAE5' : '#FEE2E2',
                    color: message.type === 'success' ? '#065F46' : '#991B1B',
                    fontSize: '14px'
                  }}>
                    {message.text}
                  </div>
                )}

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={handleCancel}
                    disabled={isLoading}
                    style={{
                      padding: '12px 24px',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#374151',
                      background: 'white',
                      border: '1px solid #D1D5DB',
                      borderRadius: '8px',
                      cursor: isLoading ? 'not-allowed' : 'pointer',
                      opacity: isLoading ? 0.6 : 1,
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      if (!isLoading) e.target.style.background = '#F9FAFB';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white';
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={isLoading}
                    style={{
                      padding: '12px 24px',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: 'white',
                      background: isLoading ? '#93C5FD' : '#3B82F6',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: isLoading ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      if (!isLoading) e.target.style.background = '#2563EB';
                    }}
                    onMouseLeave={(e) => {
                      if (!isLoading) e.target.style.background = '#3B82F6';
                    }}
                  >
                    {isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* NEW LISTINGS CHART */}
          <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '32px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '20px' }}>New Listings Overview</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={newListings}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis />
                <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* BOTTOM BLOCKS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '20px' }}>
            <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '20px' }}>Most Popular Books</h3>
              {topBooks.map((book, i) => <BookItem key={i} {...book} />)}
            </div>

            <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Sales by Category</h3>
                <p style={{ fontSize: '13px', color: '#6B7280', marginTop: '4px' }}>Sales distribution by category</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '24px', position: 'relative' }}>
                <svg width="240" height="240" viewBox="0 0 240 240" style={{ transform: 'rotate(-90deg)' }}>
                  {salesByCategory.map((cat, i) => {
                    const previousTotal = salesByCategory.slice(0, i).reduce((sum, c) => sum + c.percentage, 0);
                    const circumference = 2 * Math.PI * 80;
                    const strokeDasharray = `${(cat.percentage / 100) * circumference} ${circumference}`;
                    const strokeDashoffset = -((previousTotal / 100) * circumference);
                    return <circle key={i} cx="120" cy="120" r="80" fill="none" stroke={cat.color} strokeWidth="40" strokeDasharray={strokeDasharray} strokeDashoffset={strokeDashoffset} style={{ transition: 'all 0.3s ease' }} />;
                  })}
                </svg>
                <div style={{ position: 'absolute', textAlign: 'center', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827' }}>{totalSales}</div>
                  <div style={{ fontSize: '13px', color: '#6B7280', marginTop: '4px' }}>Total Sales</div>
                </div>
              </div>
              {salesByCategory.map((cat, i) => <CategoryItem key={i} {...cat} />)}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
