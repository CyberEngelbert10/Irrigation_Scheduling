export interface User {
  id: number;
  email: string;
  name: string;
  location?: string;
  date_joined: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  name: string;
  password: string;
  password_confirm: string;
  location?: string;
}

export interface ChangePasswordData {
  old_password: string;
  password: string;
  password2: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}
