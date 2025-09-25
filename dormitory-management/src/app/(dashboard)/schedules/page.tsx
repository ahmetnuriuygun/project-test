'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient, AttendanceSchedule } from '@/lib/api'
import { Plus, Calendar, Clock, MapPin } from 'lucide-react'
import { formatDate } from '@/lib/utils'

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<AttendanceSchedule[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        const data = await apiClient.getAttendanceSchedules()
        setSchedules(data)
      } catch (error) {
        console.error('Failed to fetch schedules:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSchedules()
  }, [])

  const getDaysOfWeek = (schedule: AttendanceSchedule) => {
    const days = []
    if (schedule.monday) days.push('Mon')
    if (schedule.tuesday) days.push('Tue')
    if (schedule.wednesday) days.push('Wed')
    if (schedule.thursday) days.push('Thu')
    if (schedule.friday) days.push('Fri')
    if (schedule.saturday) days.push('Sat')
    if (schedule.sunday) days.push('Sun')
    return days.join(', ')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading schedules...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Attendance Schedules</h1>
          <p className="text-gray-600">Manage attendance schedules and timing</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Schedule
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Schedules</CardTitle>
            <Calendar className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{schedules.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Schedules</CardTitle>
            <Clock className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {schedules.filter(s => s.is_active).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Week</CardTitle>
            <MapPin className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {schedules.filter(s => s.is_active && new Date(s.start_date) <= new Date()).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schedules List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {schedules.map((schedule) => (
          <Card key={schedule.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{schedule.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {schedule.description || 'No description provided'}
                  </CardDescription>
                </div>
                <Badge variant={schedule.is_active ? 'default' : 'secondary'}>
                  {schedule.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Start Time:</span>
                  <p className="font-medium">{schedule.start_time}</p>
                </div>
                <div>
                  <span className="text-gray-500">End Time:</span>
                  <p className="font-medium">{schedule.end_time}</p>
                </div>
              </div>

              <div>
                <span className="text-gray-500 text-sm">Days:</span>
                <p className="font-medium">{getDaysOfWeek(schedule)}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Start Date:</span>
                  <p className="font-medium">{formatDate(schedule.start_date)}</p>
                </div>
                <div>
                  <span className="text-gray-500">End Date:</span>
                  <p className="font-medium">
                    {schedule.end_date ? formatDate(schedule.end_date) : 'Ongoing'}
                  </p>
                </div>
              </div>

              {schedule.last_attendance_taken && (
                <div>
                  <span className="text-gray-500 text-sm">Last Attendance:</span>
                  <p className="font-medium">{formatDate(schedule.last_attendance_taken)}</p>
                </div>
              )}

              <div className="flex space-x-2 pt-2">
                <Button variant="outline" size="sm" className="flex-1">
                  View Details
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  Edit
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {schedules.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No schedules found</h3>
            <p className="text-gray-500">
              Get started by creating your first attendance schedule.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}