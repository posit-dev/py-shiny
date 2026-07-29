enum UserRole {
  Admin = "admin",
  Editor = "editor",
  Viewer = "viewer",
}

interface ApiResponse<T> {
  data: T;
  status: "success" | "error";
  timestamp: Date;
}

interface User {
  id: string;
  name: string;
  role: UserRole;
}

class UserService {
  private cache: Map<string, User> = new Map();
  private readonly apiUrl = "https://api.example.com";

  public async fetchUser(id: string): Promise<ApiResponse<User>> {
    if (this.cache.has(id)) {
      return this.createResponse(this.cache.get(id)!);
    }

    const response = await fetch(`${this.apiUrl}/users/${id}`);
    const user: User = await response.json();
    this.cache.set(id, user);
    return this.createResponse(user);
  }

  private createResponse<T extends User>(data: T): ApiResponse<T> {
    return { data, status: "success", timestamp: new Date() };
  }
}

const service = new UserService();
await service.fetchUser("123");
