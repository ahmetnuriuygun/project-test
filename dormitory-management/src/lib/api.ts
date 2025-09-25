const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface LoginCredentials {
  username: string
  password: string
}

export interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'staff' | 'supervisor' | 'io-device'
  phone?: string
  is_active: boolean
  dormitory_id?: string
  photo_url?: string
}

export interface Student {
  id: string
  name: string
  surname?: string
  rfid_tag: string
  date_of_birth?: string
  phone?: string
  email?: string
  school?: string
  class_name?: string
  address?: string
  city?: string
  postal_code?: string
  parent_name?: string
  parent_phone?: string
  parent_email?: string
  photo_url?: string
  dormitory_id: string
  room_id?: string
  is_active: boolean
  enrollment_date: string
  created_at: string
}

export interface Ticket {
  id: string
  title: string
  description: string
  status: 'open' | 'in_progress' | 'closed'
  assigned_student?: string
  created_by: string
  created_at: string
  updated_at?: string
  category?: string
}

export interface AttendanceSchedule {
  id: string
  name: string
  description?: string
  dormitory_id: string
  monday: boolean
  tuesday: boolean
  wednesday: boolean
  thursday: boolean
  friday: boolean
  saturday: boolean
  sunday: boolean
  start_time: string
  end_time: string
  start_date: string
  end_date?: string
  is_active: boolean
  created_at: string
  last_attendance_taken?: string
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor() {
    this.baseURL = API_BASE_URL
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(credentials: LoginCredentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Invalid credentials')
    }

    const data = await response.json()
    this.setToken(data.access_token)
    return data
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/auth/me')
  }

  async logout() {
    this.clearToken()
  }

  // Students endpoints
  async getStudents(): Promise<Student[]> {
    return this.request<Student[]>('/api/students/')
  }

  async getStudent(id: string): Promise<Student> {
    return this.request<Student>(`/api/students/${id}`)
  }

  async createStudent(student: Partial<Student>): Promise<Student> {
    return this.request<Student>('/api/students/', {
      method: 'POST',
      body: JSON.stringify(student),
    })
  }

  async updateStudent(id: string, student: Partial<Student>): Promise<Student> {
    return this.request<Student>(`/api/students/${id}`, {
      method: 'PUT',
      body: JSON.stringify(student),
    })
  }

  // Tickets endpoints
  async getTickets(): Promise<Ticket[]> {
    return this.request<Ticket[]>('/api/v1/tickets/')
  }

  async createTicket(ticket: Partial<Ticket>): Promise<Ticket> {
    return this.request<Ticket>('/api/v1/tickets/', {
      method: 'POST',
      body: JSON.stringify(ticket),
    })
  }

  async updateTicket(id: string, ticket: Partial<Ticket>): Promise<Ticket> {
    return this.request<Ticket>(`/api/v1/tickets/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(ticket),
    })
  }

  // Attendance schedules endpoints
  async getAttendanceSchedules(): Promise<AttendanceSchedule[]> {
    return this.request<AttendanceSchedule[]>('/api/attendance-schedules/')
  }

  async createAttendanceSchedule(schedule: Partial<AttendanceSchedule>): Promise<AttendanceSchedule> {
    return this.request<AttendanceSchedule>('/api/attendance-schedules/', {
      method: 'POST',
      body: JSON.stringify(schedule),
    })
  }
}

export const apiClient = new ApiClient()