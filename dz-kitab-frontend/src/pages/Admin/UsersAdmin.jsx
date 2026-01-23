import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // ← Import pour navigation
import "./UsersAdmin.css";
import NavAdmin from "./navbarAdmin";

const initialUsers = [
  { id: 1, name: "Ahmed Benali", email: "ahmed@gmail.com", role: "User", status: "active", joinedDate: "2024-01-15" },
  { id: 2, name: "Sara Kacem", email: "sara@gmail.com", role: "Admin", status: "active", joinedDate: "2023-12-10" },
  { id: 3, name: "Yanis Omar", email: "yanis@gmail.com", role: "User", status: "blocked", joinedDate: "2024-02-20" },
  { id: 4, name: "Leila Mansouri", email: "leila@gmail.com", role: "User", status: "active", joinedDate: "2024-03-05" },
];

export default function AdminUsers() {
  const navigate = useNavigate(); // ← Navigation
  useEffect(() => {
    const token = localStorage.getItem("token"); // Vérifie le token
    if (!token) {
      navigate("/login"); // Redirige vers login si pas connecté
    }
  }, [navigate]);

  const [users, setUsers] = useState(initialUsers);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterRole, setFilterRole] = useState("all");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const toggleStatus = (id) => {
    setUsers(prev =>
      prev.map(u =>
        u.id === id ? { ...u, status: u.status === "active" ? "blocked" : "active" } : u
      )
    );
  };

  const deleteUser = (id) => {
    setUsers(prev => prev.filter(u => u.id !== id));
  };

  let filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(search.toLowerCase()) ||
                          user.email.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = filterStatus === "all" || user.status === filterStatus;
    const matchesRole = filterRole === "all" || user.role === filterRole;
    return matchesSearch && matchesStatus && matchesRole;
  });

  filteredUsers = filteredUsers.sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];

    if (sortBy === "joinedDate") {
      aVal = new Date(aVal);
      bVal = new Date(bVal);
    }

    if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
    if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });

  const stats = {
    total: users.length,
    active: users.filter(u => u.status === "active").length,
    blocked: users.filter(u => u.status === "blocked").length,
    admins: users.filter(u => u.role === "Admin").length,
    normalUsers: users.filter(u => u.role === "User").length,
  };

  return (
    <>
      <NavAdmin />
      <div className="admin-page">
        <h1 className="admin-title">Users Management</h1>

        {/* Stats Cards */}
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Users</div>
          </div>
          <div className="stat-card stat-success">
            <div className="stat-value">{stats.active}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card stat-danger">
            <div className="stat-value">{stats.blocked}</div>
            <div className="stat-label">Blocked</div>
          </div>
          <div className="stat-card stat-info">
            <div className="stat-value">{stats.admins}</div>
            <div className="stat-label">Admins</div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="admin-search">
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Filters */}
        <div className="filter-group">
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="filter-select">
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="blocked">Blocked</option>
          </select>

          <select value={filterRole} onChange={(e) => setFilterRole(e.target.value)} className="filter-select">
            <option value="all">All Roles</option>
            <option value="User">User</option>
            <option value="Admin">Admin</option>
          </select>
        </div>

        {/* Table */}
        <div className="admin-card">
          <div className="table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort("name")} className="sortable">
                    Name {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th onClick={() => handleSort("email")} className="sortable">
                    Email {sortBy === "email" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th>Role</th>
                  <th onClick={() => handleSort("status")} className="sortable">
                    Status {sortBy === "status" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th onClick={() => handleSort("joinedDate")} className="sortable">
                    Joined {sortBy === "joinedDate" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length > 0 ? (
                  filteredUsers.map(user => (
                    <tr key={user.id}>
                      <td data-label="Name">
                        <div className="user-name">
                          <div className="user-avatar">{user.name.charAt(0)}</div>
                          {user.name}
                        </div>
                      </td>
                      <td data-label="Email">{user.email}</td>
                      <td data-label="Role">
                        <span className={`role role-${user.role.toLowerCase()}`}>{user.role}</span>
                      </td>
                      <td data-label="Status">
                        <span className={`status ${user.status}`}>
                          {user.status === "active" ? "✓ Active" : "✗ Blocked"}
                        </span>
                      </td>
                      <td data-label="Joined">{new Date(user.joinedDate).toLocaleDateString('fr-DZ')}</td>
                      <td data-label="Actions">
                        <div className="actions">
                          <button 
                            className="btn btn-toggle" 
                            onClick={() => toggleStatus(user.id)}
                            title={user.status === "active" ? "Block user" : "Activate user"}
                            disabled={user.role === "Admin"}
                            style={{ opacity: user.role === "Admin" ? 0.5 : 1, cursor: user.role === "Admin" ? "not-allowed" : "pointer" }}
                          >
                            {user.status === "active" ? "Block" : "Activate"}
                          </button>
                          <button 
                            className="btn btn-delete" 
                            onClick={() => deleteUser(user.id)}
                            title="Delete user"
                            disabled={user.role === "Admin"}
                            style={{ opacity: user.role === "Admin" ? 0.5 : 1, cursor: user.role === "Admin" ? "not-allowed" : "pointer" }}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan="6" className="no-data">No users found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Results Info */}
        <div className="results-info">
          Showing {filteredUsers.length} users — {stats.normalUsers} User(s), {stats.admins} Admin(s)
        </div>
      </div>
    </>
  );
}
