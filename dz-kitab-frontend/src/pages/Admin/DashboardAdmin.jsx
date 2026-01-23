import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from "recharts";
import NavAdmin from "./navbarAdmin";

// --- Données Mockées ---
const newListingsData = [
  { month: "Jan", value: 234 }, { month: "Feb", value: 267 }, { month: "Mar", value: 298 }, 
  { month: "Apr", value: 312 }, { month: "May", value: 345 }, { month: "Jun", value: 378 },
  { month: "Jul", value: 402 }, { month: "Aug", value: 389 }, { month: "Sep", value: 421 },
  { month: "Oct", value: 445 }, { month: "Nov", value: 467 }, { month: "Dec", value: 489 },
];

const miniChartData1 = [{ value: 1050 }, { value: 1120 }, { value: 1180 }, { value: 1247 }, { value: 1310 }, { value: 1389 }];
const miniChartData2 = [{ value: 3456 }, { value: 3598 }, { value: 3712 }, { value: 3845 }, { value: 3892 }, { value: 4021 }];

const topBooks = [
  { title: "Python Algorithms", category: "Computer Science", listings: 47, image: "https://images.unsplash.com/photo-1589998059171-988d887df646?w=80&h=80&fit=crop", percentage: 98 },
  { title: "Mathematics 1st Year", category: "Academic", listings: 42, image: "https://images.unsplash.com/photo-1596495577886-d920f1fb7238?w=80&h=80&fit=crop", percentage: 89 },
  { title: "Physics Senior Year", category: "Academic", listings: 38, image: "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=80&h=80&fit=crop", percentage: 81 },
  { title: "Introduction to React", category: "Computer Science", listings: 35, image: "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=80&h=80&fit=crop", percentage: 74 },
  { title: "Algerian History", category: "History", listings: 31, image: "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=80&h=80&fit=crop", percentage: 66 },
  { title: "Organic Chemistry", category: "Science", listings: 28, image: "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=80&h=80&fit=crop", percentage: 60 },
];

const salesByCategory = [
  { name: "Computer Science", value: 1247, color: "#3B82F6", percentage: 31 },
  { name: "Academic", value: 1089, color: "#10B981", percentage: 27 },
  { name: "Science", value: 845, color: "#F59E0B", percentage: 21 },
  { name: "Literature", value: 562, color: "#8B5CF6", percentage: 14 },
  { name: "History", value: 278, color: "#EF4444", percentage: 7 },
];

const totalSales = salesByCategory.reduce((sum, cat) => sum + cat.value, 0);

// --- Composants ---
function MetricCard({ title, value, chart }) {
  return (
    <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>{title}</div>
      <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '12px' }}>{value}</div>
      <div style={{ height: '60px' }}>
        {chart ? chart : <div style={{ background: '#F3F4F6', height: '100%', borderRadius: '4px' }} />}
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

// --- Composant principal ---
export default function AdminDashboard() {
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

          {/* --- BLOC DU HAUT --- */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '20px', marginBottom: '32px' }}>
            <MetricCard title="Total Users" value="1,389" />
            <MetricCard title="Total Listings" value="4,021" />
            <MetricCard title="Active listings" value={8} />
            <MetricCard title="Active Users (30d)" value="1,127" chart={<MiniLineChart data={miniChartData1} />} />
            <MetricCard title="New Listings (30d)" value="489" chart={<MiniLineChart data={miniChartData2} />} />
          </div>

          {/* New Listings Overview */}
          <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '32px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '20px' }}>New Listings Overview</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={newListingsData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis />
                <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* --- BLOC DU BAS --- */}
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
