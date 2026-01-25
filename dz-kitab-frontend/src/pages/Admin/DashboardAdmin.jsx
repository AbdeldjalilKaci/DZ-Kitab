import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from "recharts";
import NavAdmin from "./navbarAdmin";
import api from "../../utils/api";

// --- Empty Data for Initial State ---
const initialMetrics = {
  totalUsers: 0,
  totalListings: 0,
  activeListings: 0,
  activeUsers30d: 0,
  newListings30d: 0,
  activeUsersTrend: [],
  newListingsTrend: []
};

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
      <img src={image || 'https://via.placeholder.com/60'} alt={title} style={{ width: '60px', height: '60px', borderRadius: '8px', objectFit: 'cover' }} />
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

// --- Main component ---
export default function AdminDashboard() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(initialMetrics);
  const [newListings, setNewListings] = useState([]);
  const [topBooks, setTopBooks] = useState([]);
  const [salesByCategory, setSalesByCategory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch Dashboard Stats
        const statsRes = await api.get('/api/admin/stats/dashboard');
        const stats = statsRes.data;

        // Map backend stats to frontend structure
        setMetrics({
          totalUsers: stats.users.total,
          totalListings: stats.announcements.total,
          activeListings: stats.announcements.active,
          activeUsers30d: stats.users.active, // Approximation using 'active' status count
          newListings30d: stats.announcements.new_this_week, // Using weekly data as proxy for now
          // Placeholder trends (backend doesn't provide detailed history yet)
          activeUsersTrend: [{ value: 0 }, { value: stats.users.active }],
          newListingsTrend: [{ value: 0 }, { value: stats.announcements.new_this_week }]
        });

        // Fetch Popular Books
        const popRes = await api.get('/api/admin/stats/popular-books?limit=5');
        setTopBooks(popRes.data.books.map(b => ({
          title: b.title,
          category: b.category,
          listings: b.listings,
          percentage: b.percentage,
          image: null // Add image if available in book object later
        })));

        // Fetch Sales By Category
        const salesRes = await api.get('/api/admin/stats/sales-by-category');
        const colors = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"];
        setSalesByCategory(salesRes.data.categories.map((c, idx) => ({
          name: c.category,
          value: c.count,
          percentage: c.percentage,
          color: colors[idx % colors.length]
        })));

        // Mock chart data for New Listings Overview (since backend doesn't give monthly data yet)
        setNewListings([
          { month: "Jan", value: 0 }, { month: "Feb", value: 0 }, { month: "Mar", value: 0 },
          { month: "Apr", value: 0 }, { month: "May", value: 0 }, { month: "Jun", value: 0 },
          { month: "Jul", value: 0 }, { month: "Aug", value: 0 }, { month: "Sep", value: 0 },
          { month: "Oct", value: 0 }, { month: "Nov", value: 0 }, { month: "Dec", value: 0 }
        ]);

      } catch (error) {
        console.error("Error fetching admin dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const totalSales = salesByCategory.reduce((sum, cat) => sum + cat.value, 0);

  if (loading) {
    return (
      <>
        <NavAdmin />
        <div style={{ padding: '40px', textAlign: 'center' }}>Loading Dashboard...</div>
      </>
    )
  }

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
            <MetricCard title="Active Users" value={metrics.activeUsers30d} chart={<MiniLineChart data={metrics.activeUsersTrend} />} />
            <MetricCard title="New Listings (Week)" value={metrics.newListings30d} chart={<MiniLineChart data={metrics.newListingsTrend} />} />
          </div>

          {/* NEW LISTINGS CHART */}
          <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '32px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '20px' }}>New Listings Overview (Mock Data)</h3>
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
              {topBooks.length > 0 ? topBooks.map((book, i) => <BookItem key={i} {...book} />) : <p>No popular books yet.</p>}
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
