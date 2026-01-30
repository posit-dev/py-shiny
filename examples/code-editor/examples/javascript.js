// Fetch user data from API and process results
class DataProcessor {
  constructor(apiUrl) {
    this.apiUrl = apiUrl;
  }

  async fetchUsers(ids) {
    try {
      const response = await fetch(this.apiUrl);
      const { users } = await response.json();

      // Filter and transform user data
      return users
        .filter(user => ids.includes(user.id))
        .map(({ id, name, email }) => ({
          id,
          displayName: `${name} (${email})`,
          active: user.status === 'active'
        }));
    } catch (error) {
      console.error(`Failed to fetch users: ${error.message}`);
      return [];
    }
  }

  processMetrics = (data) => {
    const stats = data.reduce((acc, item) => ({
      ...acc,
      total: (acc.total || 0) + item.value
    }), {});
    return stats;
  }
}

const processor = new DataProcessor('https://api.example.com/users');
