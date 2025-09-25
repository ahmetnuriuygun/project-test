'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Building, Users, MapPin, Plus } from 'lucide-react'

export default function DormitoriesPage() {
  // Mock data for demonstration
  const dormitories = [
    {
      id: 1,
      name: 'Sint-Victor Internaat',
      address: 'Kasteelplein 20, 2300 Turnhout',
      students: 25,
      staff: 5,
      rooms: 15,
      isActive: true
    },
    {
      id: 2,
      name: 'Sint-Jan Internaat',
      address: 'Collegestraat 27, 2300 Turnhout',
      students: 30,
      staff: 6,
      rooms: 18,
      isActive: true
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dormitories</h1>
          <p className="text-gray-600">Manage dormitory facilities and information</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Dormitory
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Dormitories</CardTitle>
            <Building className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dormitories.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <Users className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dormitories.reduce((sum, dorm) => sum + dorm.students, 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Rooms</CardTitle>
            <Building className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dormitories.reduce((sum, dorm) => sum + dorm.rooms, 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dormitories List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {dormitories.map((dormitory) => (
          <Card key={dormitory.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Building className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{dormitory.name}</CardTitle>
                    <CardDescription className="flex items-center mt-1">
                      <MapPin className="h-4 w-4 mr-1" />
                      {dormitory.address}
                    </CardDescription>
                  </div>
                </div>
                <Badge variant={dormitory.isActive ? 'default' : 'secondary'}>
                  {dormitory.isActive ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{dormitory.students}</div>
                  <div className="text-sm text-gray-500">Students</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{dormitory.staff}</div>
                  <div className="text-sm text-gray-500">Staff</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{dormitory.rooms}</div>
                  <div className="text-sm text-gray-500">Rooms</div>
                </div>
              </div>

              <div className="flex space-x-2 pt-2">
                <Button variant="outline" size="sm" className="flex-1">
                  View Details
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  Manage
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common dormitory management tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex-col">
              <Users className="h-6 w-6 mb-2" />
              Manage Students
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Building className="h-6 w-6 mb-2" />
              Room Assignment
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <MapPin className="h-6 w-6 mb-2" />
              Facility Reports
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}