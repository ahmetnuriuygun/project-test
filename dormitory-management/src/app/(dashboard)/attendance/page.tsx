'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { UserCheck, Clock, AlertTriangle, CheckCircle } from 'lucide-react'

export default function AttendancePage() {
  // Mock data for demonstration
  const attendanceStats = {
    present: 45,
    absent: 3,
    late: 2,
    total: 50
  }

  const recentAttendance = [
    { id: 1, student: 'John Doe', status: 'present', time: '08:15', schedule: 'Morning Check' },
    { id: 2, student: 'Jane Smith', status: 'late', time: '08:25', schedule: 'Morning Check' },
    { id: 3, student: 'Mike Johnson', status: 'absent', time: '-', schedule: 'Morning Check' },
    { id: 4, student: 'Sarah Wilson', status: 'present', time: '08:10', schedule: 'Morning Check' },
    { id: 5, student: 'Tom Brown', status: 'present', time: '08:05', schedule: 'Morning Check' },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'late':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'absent':
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      default:
        return <UserCheck className="h-4 w-4" />
    }
  }

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'present':
        return 'default'
      case 'late':
        return 'secondary'
      case 'absent':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Attendance</h1>
          <p className="text-gray-600">Monitor student attendance and check-ins</p>
        </div>
        <Button>
          <UserCheck className="h-4 w-4 mr-2" />
          Take Attendance
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Present</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{attendanceStats.present}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((attendanceStats.present / attendanceStats.total) * 100)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Late</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{attendanceStats.late}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((attendanceStats.late / attendanceStats.total) * 100)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Absent</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{attendanceStats.absent}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((attendanceStats.absent / attendanceStats.total) * 100)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Attendance Rate</CardTitle>
            <UserCheck className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(((attendanceStats.present + attendanceStats.late) / attendanceStats.total) * 100)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Todays rate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Attendance */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Attendance</CardTitle>
          <CardDescription>Latest check-ins and attendance records</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentAttendance.map((record) => (
              <div key={record.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(record.status)}
                  <div>
                    <p className="font-medium">{record.student}</p>
                    <p className="text-sm text-gray-500">{record.schedule}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-medium">{record.time}</p>
                    <p className="text-xs text-gray-500">Check-in time</p>
                  </div>
                  <Badge variant={getStatusVariant(record.status)}>
                    {record.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common attendance tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start">
              <UserCheck className="h-4 w-4 mr-2" />
              Take Morning Attendance
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Clock className="h-4 w-4 mr-2" />
              Mark Late Arrivals
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Report Absences
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Todays Schedule</CardTitle>
            <CardDescription>Upcoming attendance checks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <div>
                <p className="font-medium">Morning Check</p>
                <p className="text-sm text-gray-600">07:00 - 08:30</p>
              </div>
              <Badge variant="default">Completed</Badge>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <div>
                <p className="font-medium">Evening Check</p>
                <p className="text-sm text-gray-600">21:00 - 22:30</p>
              </div>
              <Badge variant="outline">Upcoming</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}