# Frontend Dashboard

React + TypeScript dashboard for monitoring and controlling the job automation system.

## Directory Structure

### `/src/components`
Reusable UI components:
- `JobCard.tsx` - Job listing display
- `ResumePreview.tsx` - Tailored resume preview
- `ApplicationTable.tsx` - Application history table
- `MatchScoreBadge.tsx` - Visual match score indicator
- `Layout/` - Navigation, header, sidebar components

### `/src/pages`
Page-level components:
- `Dashboard.tsx` - Main overview page
- `Jobs.tsx` - Job listings with filters
- `Applications.tsx` - Application tracking
- `Resumes.tsx` - Resume management
- `Settings.tsx` - User preferences

### `/src/hooks`
Custom React hooks:
- `useJobs.ts` - Job data fetching/mutations
- `useApplications.ts` - Application state management
- `useAuth.ts` - Authentication state

### `/src/services`
API client services:
- `api.ts` - Axios/Fetch configuration
- `jobService.ts` - Job-related API calls
- `resumeService.ts` - Resume API calls

### `/src/types`
TypeScript type definitions:
- `job.types.ts`
- `application.types.ts`
- `resume.types.ts`

### `/src/utils`
Frontend utilities:
- `formatters.ts` - Date/currency formatting
- `validators.ts` - Form validation
- `constants.ts` - UI constants

### `/public`
Static assets (images, icons, fonts)
