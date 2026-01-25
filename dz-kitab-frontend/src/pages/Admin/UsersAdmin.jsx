import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // ← Import pour navigation
import "./UsersAdmin.css";
import NavAdmin from "./navbarAdmin";
import api from "../../utils/api";

export default function AdminUsers() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterRole, setFilterRole] = useState("all");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch Users
  const fetchUsers = async () => {
    setLoading(true);
    try {
      // Construct query params
      const params = { limit: 100 };
      if (search) params.search = search;
      if (filterStatus !== 'all') params.status = filterStatus;
      if (filterRole !== 'all') params.role = filterRole.toLowerCase();

      const response = await api.get('/api/admin/users', { params });

      // Map backend user format to frontend format
      const mappedUsers = response.data.users.map(u => ({
        id: u.id,
        name: u.username, // Using username as name
        email: u.email,
        role: u.role,
        status: u.is_active ? "active" : "blocked",
        joinedDate: u.created_at
      }));
      setUsers(mappedUsers);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [search, filterStatus, filterRole]); // Re-fetch when filters change (debouncing would be better for search)

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const toggleStatus = async (id, currentStatus) => {
    try {
      if (currentStatus === "active") {
        await api.put(`/api/admin/users/${id}/block`);
      } else {
        await api.put(`/api/admin/users/${id}/activate`);
      }
      // Refresh list
      fetchUsers();
    } catch (error) {
      console.error("Error toggling user status:", error);
      alert("Failed to update user status");
    }
  };

  const deleteUser = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await api.delete(`/api/admin/users/${id}`);
      fetchUsers();
    } catch (error) {
      console.error("Error deleting user:", error);
      alert("Failed to delete user");
    }
  };

  // Local sorting (can also be done on backend if needed)
  let sortedUsers = [...users].sort((a, b) => {
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
            {loading ? (
              <div style={{ padding: '20px', textAlign: 'center' }}>Loading users...</div>
            ) : (
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
                  {sortedUsers.length > 0 ? (
                    sortedUsers.map(user => (
                      <tr key={user.id}>
                        <td data-label="Name">
                          <div className="user-name">
                            <div className="user-avatar">{user.name.charAt(0).toUpperCase()}</div>
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
                              onClick={() => toggleStatus(user.id, user.status)}
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
            )}
          </div>
        </div>

        {/* Results Info */}
        <div className="results-info">
          Showing {sortedUsers.length} users — {stats.normalUsers} User(s), {stats.admins} Admin(s)
        </div>
      </div>
    </>
  );
}
