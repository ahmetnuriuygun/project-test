# Dormitory Management System Frontend

A modern Next.js frontend for the Dormitory Management System, built with TypeScript, Tailwind CSS, and designed to work with the FastAPI backend.

## Features

- **Authentication**: Secure login system integrated with FastAPI backend
- **Student Management**: View, search, and manage student records
- **Attendance Tracking**: Monitor attendance schedules and records
- **Ticket System**: Create and manage support tickets
- **Dormitory Management**: Oversee dormitory facilities and information
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Headless UI
- **Icons**: Lucide React
- **Authentication**: Integration with Supabase Auth (planned)
- **Storage**: Supabase Storage (planned)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Running FastAPI backend (see backend repository)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd dormitory-management
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:
```env
# FastAPI Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration (for future use)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Demo Credentials

For testing purposes, you can use these demo credentials:
- **Email**: admin1@internaat.be
- **Password**: password

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (dashboard)/       # Dashboard layout group
│   │   ├── dashboard/     # Dashboard page
│   │   ├── students/      # Students management
│   │   ├── attendance/    # Attendance tracking
│   │   ├── schedules/     # Schedule management
│   │   ├── tickets/       # Ticket system
│   │   ├── dormitories/   # Dormitory management
│   │   └── settings/      # System settings
│   ├── login/             # Login page
│   └── layout.tsx         # Root layout
├── components/            # Reusable components
│   ├── ui/               # UI components
│   └── layout/           # Layout components
├── lib/                  # Utilities and configurations
│   ├── api.ts           # API client
│   ├── supabase.ts      # Supabase configuration
│   └── utils.ts         # Utility functions
└── styles/              # Global styles
```

## API Integration

The frontend integrates with the FastAPI backend through a centralized API client (`src/lib/api.ts`). Key features:

- **Authentication**: JWT token management
- **Students**: CRUD operations for student records
- **Tickets**: Support ticket management
- **Attendance**: Schedule and record management
- **Error Handling**: Centralized error handling

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically on push

### Manual Deployment

1. Build the application:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

## Backend Integration

This frontend is designed to work with the FastAPI backend. Make sure your backend is running and accessible at the URL specified in `NEXT_PUBLIC_API_URL`.

### Backend Requirements

- FastAPI backend running on specified URL
- CORS configured to allow frontend domain
- Authentication endpoints available
- All API endpoints as documented in the backend

## Future Enhancements

- **Supabase Integration**: Full authentication and storage integration
- **Real-time Updates**: WebSocket integration for live updates
- **Mobile App**: React Native version
- **Advanced Analytics**: Detailed reporting and analytics
- **Offline Support**: PWA capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.