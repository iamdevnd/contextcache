import { create } from 'zustand';
import api from '../api';
import { endpoints } from '../config';
import Cookies from 'js-cookie';
import toast from 'react-hot-toast';

interface User {
  username: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

interface RegisterData {
  username: string;
  password: string;
  email: string;
  accept_terms: boolean;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  isAuthenticated: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post(endpoints.auth.login, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { access_token } = response.data;
      Cookies.set('access_token', access_token, { expires: 1 });

      await useAuthStore.getState().checkAuth();
      toast.success('Login successful!');
    } catch (error) {
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (data: RegisterData) => {
    set({ isLoading: true });
    try {
      await api.post(endpoints.auth.register, data);
      toast.success('Registration successful! Please login.');
    } catch (error) {
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    try {
      await api.post(endpoints.auth.logout);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      Cookies.remove('access_token');
      set({ user: null, isAuthenticated: false });
      window.location.href = '/login';
    }
  },

  checkAuth: async () => {
    const token = Cookies.get('access_token');
    if (!token) {
      set({ user: null, isAuthenticated: false });
      return;
    }

    try {
      const response = await api.get(endpoints.auth.me);
      set({ user: response.data, isAuthenticated: true });
    } catch (error) {
      Cookies.remove('access_token');
      set({ user: null, isAuthenticated: false });
    }
  },
}));
