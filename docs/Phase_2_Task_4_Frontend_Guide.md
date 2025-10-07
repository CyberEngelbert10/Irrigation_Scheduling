# Phase 2 Task 4: Frontend Development Guide

**Status:** 🔄 IN PROGRESS  
**Started:** October 7, 2025  
**Backend Status:** ✅ Complete (all 28 tests passing)

---

## Overview

Build user-friendly frontend pages for Field Management that interact with the completed backend API. Focus on farmer-friendly UI with clear forms, validations, and feedback.

---

## Pages to Build

### 1. Fields List Page (`/fields`)
**Route:** `frontend/src/pages/fields/index.tsx`

**Features:**
- Display all user's fields in grid/card layout
- Show key info: name, crop type, area, planting date, status
- Filters: active status, crop type, region
- Search bar: search by name or location
- "Add Field" button
- Quick actions on each card: Edit, Delete, View Details
- Empty state: "No fields yet, add your first field"
- Loading state while fetching data

**API Integration:**
- `GET /api/fields/` - Fetch all fields
- `GET /api/fields/?crop_type=Maize` - Filter by crop
- `GET /api/fields/?search=North` - Search
- `DELETE /api/fields/{id}/` - Delete field

**Components Needed:**
- `FieldCard` - Individual field display
- `FieldFilters` - Filter dropdowns
- `SearchBar` - Search input
- `EmptyState` - When no fields exist
- `DeleteConfirmModal` - Confirm delete action

---

### 2. Add Field Page (`/fields/new`)
**Route:** `frontend/src/pages/fields/new.tsx`

**Features:**
- Form with all field inputs
- Validation matching backend rules
- Dropdowns populated with choices
- Date picker for planting date
- Optional fields (latitude, longitude, notes)
- Submit button with loading state
- Cancel button to go back
- Success toast notification
- Error display for validation failures

**Form Fields:**
```typescript
{
  name: string;              // Required, max 255 chars
  location: string;          // Optional
  region: string;            // Required, dropdown (10 provinces)
  latitude: number;          // Optional, -90 to 90
  longitude: number;         // Optional, -180 to 180
  area: number;              // Required, > 0
  crop_type: string;         // Required, dropdown (6 crops)
  planting_date: date;       // Required, not in future
  soil_type: string;         // Required, dropdown (4 types)
  current_soil_moisture: number; // Required, 0-100
  irrigation_method: string; // Required, dropdown (4 methods)
  current_season: string;    // Required, dropdown (2 seasons)
  notes: string;             // Optional, textarea
  is_active: boolean;        // Default true, checkbox
}
```

**Dropdown Choices:**
- **Regions:** Lusaka, Central Province, Southern Province, Eastern Province, Copperbelt, Northern Province, Western Province, Luapula Province, Muchinga Province, North-Western Province
- **Crops:** Maize, Wheat, Rice, Tomatoes, Potatoes, Cotton
- **Soil Types:** Clay, Loam, Sandy, Silty
- **Irrigation Methods:** Drip, Sprinkler, Flood, Rainfed
- **Seasons:** Dry (May-October), Wet (November-April)

**Validation Rules:**
- Name: required, max 255 chars
- Region: required, must be valid choice
- Area: required, > 0, numeric
- Crop Type: required, must be valid choice
- Planting Date: required, cannot be in future
- Soil Type: required, must be valid choice
- Soil Moisture: required, 0-100, integer
- Irrigation Method: required, must be valid choice
- Season: required, must be valid choice

**API Integration:**
- `POST /api/fields/` - Create new field

**Error Handling:**
- Display backend validation errors under each field
- Show generic error toast if request fails
- Disable submit button while submitting

---

### 3. Edit Field Page (`/fields/[id]/edit`)
**Route:** `frontend/src/pages/fields/[id]/edit.tsx`

**Features:**
- Same form as Add Field
- Pre-populate with existing field data
- Same validation rules
- Update button instead of Create
- Success toast and redirect to fields list
- Handle 404 if field doesn't exist or belongs to other user

**API Integration:**
- `GET /api/fields/{id}/` - Fetch field details
- `PATCH /api/fields/{id}/` - Update field

---

### 4. Field Details Page (`/fields/[id]`)
**Route:** `frontend/src/pages/fields/[id]/index.tsx`

**Features:**
- Display all field information in readable format
- Show computed values: crop days, crop age (weeks)
- Show display names for choices (e.g., "Lusaka" not "lusaka")
- Status badge (Active/Inactive)
- Action buttons: Edit, Delete, Update Moisture
- Breadcrumb navigation
- Link to AI schedule (Phase 4)

**Display Sections:**
1. **Basic Info:** Name, Location, Status
2. **Crop Details:** Type, Planting Date, Days Since Planting, Age (weeks)
3. **Field Details:** Area, Region, Coordinates (if available)
4. **Soil & Water:** Soil Type, Current Moisture, Irrigation Method
5. **Season & Notes:** Current Season, Additional Notes

**API Integration:**
- `GET /api/fields/{id}/` - Fetch field details
- `DELETE /api/fields/{id}/` - Delete field
- `PATCH /api/fields/{id}/update-moisture/` - Update moisture

**Components Needed:**
- `FieldDetailCard` - Section for each category
- `UpdateMoistureModal` - Quick moisture update
- `DeleteConfirmModal` - Confirm delete

---

### 5. Update Moisture Modal (Component)
**Component:** `frontend/src/components/fields/UpdateMoistureModal.tsx`

**Features:**
- Modal overlay
- Single input: current_soil_moisture (0-100)
- Validation: 0-100, integer
- Submit button with loading state
- Cancel button
- Success toast on update
- Error display

**API Integration:**
- `PATCH /api/fields/{id}/update-moisture/` - Update moisture only

---

## TypeScript Types

Create `frontend/src/types/field.ts`:

```typescript
export interface Field {
  id: number;
  user_email: string;
  user_name: string;
  name: string;
  location?: string;
  region: string;
  region_display: string;
  latitude?: number;
  longitude?: number;
  area: number;
  crop_type: string;
  crop_type_display: string;
  planting_date: string; // ISO date string
  crop_days: number;
  crop_age_weeks: number;
  soil_type: string;
  soil_type_display: string;
  current_soil_moisture: number;
  irrigation_method: string;
  irrigation_method_display: string;
  current_season: string;
  season_display: string;
  notes?: string;
  is_active: boolean;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface FieldCreateData {
  name: string;
  location?: string;
  region: string;
  latitude?: number;
  longitude?: number;
  area: number;
  crop_type: string;
  planting_date: string;
  soil_type: string;
  current_soil_moisture: number;
  irrigation_method: string;
  current_season: string;
  notes?: string;
  is_active: boolean;
}

export interface FieldUpdateData extends Partial<FieldCreateData> {}

export interface FieldListItem {
  id: number;
  name: string;
  crop_type: string;
  region_display: string;
  area: number;
  is_active: boolean;
}

export interface FieldStatistics {
  total_fields: number;
  active_fields: number;
  inactive_fields: number;
  total_area_hectares: number;
  crop_distribution: Record<string, number>;
  region_distribution: Record<string, number>;
}

export const REGIONS = [
  { value: 'lusaka', label: 'Lusaka' },
  { value: 'central', label: 'Central Province' },
  { value: 'southern', label: 'Southern Province' },
  { value: 'eastern', label: 'Eastern Province' },
  { value: 'copperbelt', label: 'Copperbelt' },
  { value: 'northern', label: 'Northern Province' },
  { value: 'western', label: 'Western Province' },
  { value: 'luapula', label: 'Luapula Province' },
  { value: 'muchinga', label: 'Muchinga Province' },
  { value: 'northwestern', label: 'North-Western Province' },
] as const;

export const CROPS = [
  { value: 'Maize', label: 'Maize' },
  { value: 'Wheat', label: 'Wheat' },
  { value: 'Rice', label: 'Rice' },
  { value: 'Tomatoes', label: 'Tomatoes' },
  { value: 'Potatoes', label: 'Potatoes' },
  { value: 'Cotton', label: 'Cotton' },
] as const;

export const SOIL_TYPES = [
  { value: 'Clay', label: 'Clay' },
  { value: 'Loam', label: 'Loam' },
  { value: 'Sandy', label: 'Sandy' },
  { value: 'Silty', label: 'Silty' },
] as const;

export const IRRIGATION_METHODS = [
  { value: 'drip', label: 'Drip Irrigation' },
  { value: 'sprinkler', label: 'Sprinkler' },
  { value: 'flood', label: 'Flood Irrigation' },
  { value: 'rainfed', label: 'Rainfed (No Irrigation)' },
] as const;

export const SEASONS = [
  { value: 'Dry', label: 'Dry Season (May-October)' },
  { value: 'Wet', label: 'Wet Season (November-April)' },
] as const;
```

---

## API Client Methods

Add to `frontend/src/lib/api.ts`:

```typescript
import { Field, FieldCreateData, FieldUpdateData, FieldStatistics } from '@/types/field';

// Field Management API
export const fieldAPI = {
  // List all user's fields
  async list(params?: {
    is_active?: boolean;
    crop_type?: string;
    region?: string;
    search?: string;
  }): Promise<Field[]> {
    const response = await api.get('/api/fields/', { params });
    return response.data;
  },

  // Get field by ID
  async get(id: number): Promise<Field> {
    const response = await api.get(`/api/fields/${id}/`);
    return response.data;
  },

  // Create new field
  async create(data: FieldCreateData): Promise<Field> {
    const response = await api.post('/api/fields/', data);
    return response.data;
  },

  // Update field (partial)
  async update(id: number, data: FieldUpdateData): Promise<Field> {
    const response = await api.patch(`/api/fields/${id}/`, data);
    return response.data;
  },

  // Delete field
  async delete(id: number): Promise<void> {
    await api.delete(`/api/fields/${id}/`);
  },

  // Update soil moisture only
  async updateMoisture(id: number, moisture: number): Promise<Field> {
    const response = await api.patch(`/api/fields/${id}/update-moisture/`, {
      current_soil_moisture: moisture,
    });
    return response.data;
  },

  // Get field statistics
  async getStatistics(): Promise<FieldStatistics> {
    const response = await api.get('/api/fields/statistics/');
    return response.data;
  },

  // Get AI model input
  async getAIInput(id: number, weatherData: {
    temperature: number;
    humidity: number;
    rainfall: number;
    windspeed: number;
  }): Promise<any> {
    const response = await api.get(`/api/fields/${id}/ai-input/`, {
      params: weatherData,
    });
    return response.data;
  },
};
```

---

## UI/UX Guidelines

### Design Principles
1. **Farmer-Friendly:** Use clear labels, large touch targets, simple language
2. **Mobile-First:** Most farmers will use mobile devices
3. **Visual Feedback:** Loading states, success/error messages, confirmation dialogs
4. **Accessibility:** WCAG 2.1 AA compliant (labels, contrast, keyboard nav)
5. **Performance:** Optimize images, lazy load, minimize API calls

### Color Scheme (Tailwind)
- **Primary:** green-600 (agriculture theme)
- **Success:** green-500
- **Error:** red-500
- **Warning:** yellow-500
- **Info:** blue-500
- **Background:** gray-50
- **Cards:** white with shadow

### Components
- **Forms:** Use consistent styling, clear labels, inline errors
- **Buttons:** Primary (green), Secondary (gray), Danger (red)
- **Cards:** Rounded corners, subtle shadow, hover effect
- **Modals:** Centered overlay, close button, focus trap
- **Toasts:** Top-right corner, auto-dismiss after 3-5 seconds

---

## Testing Checklist

### Functionality
- [ ] Fields list displays all user fields
- [ ] Add field form validates all inputs
- [ ] Add field creates field successfully
- [ ] Edit field form pre-populates correctly
- [ ] Edit field updates field successfully
- [ ] Delete field shows confirmation
- [ ] Delete field removes field
- [ ] Field details displays all information
- [ ] Update moisture modal works
- [ ] Filters work (crop type, region, active)
- [ ] Search works (name, location)
- [ ] Empty state displays when no fields
- [ ] Loading states display during API calls
- [ ] Success toasts appear after actions
- [ ] Error messages display for validation failures
- [ ] 404 handling for non-existent fields

### Security
- [ ] Unauthenticated users redirected to login
- [ ] Users cannot access other users' fields
- [ ] JWT token sent with all requests
- [ ] Token refresh works

### UI/UX
- [ ] Responsive design works on mobile (320px+)
- [ ] All interactive elements keyboard accessible
- [ ] Form labels associated with inputs
- [ ] Color contrast meets WCAG AA
- [ ] Loading spinners/skeletons display
- [ ] Hover states on interactive elements
- [ ] Consistent spacing and typography

### Edge Cases
- [ ] Long field names truncate properly
- [ ] Large numbers of fields (100+) handled
- [ ] Network errors handled gracefully
- [ ] Slow network shows loading states
- [ ] Back button works correctly
- [ ] Page refresh maintains auth state

---

## Implementation Order

1. **TypeScript Types** - Define Field interfaces and constants
2. **API Client Methods** - Add fieldAPI to api.ts
3. **Fields List Page** - Start with simple list, add filters later
4. **Add Field Page** - Build form with validation
5. **Field Details Page** - Display field information
6. **Edit Field Page** - Reuse Add Field form component
7. **Update Moisture Modal** - Quick action component
8. **Delete Confirmation Modal** - Reusable modal
9. **Polish & Testing** - Refinements, error handling, loading states

---

## Success Criteria

✅ User can view all their fields  
✅ User can add a new field via form  
✅ User can edit existing field  
✅ User can delete field with confirmation  
✅ User can update soil moisture quickly  
✅ Validation works and matches backend  
✅ Success/error messages display properly  
✅ Loading states show during API calls  
✅ Responsive design works on mobile  
✅ All forms are accessible (keyboard, screen readers)  

---

## Next Steps After Frontend

Once frontend is complete, proceed to:
- **Task 5:** End-to-End Testing (create, view, edit, delete fields)
- **Phase 3:** Weather Integration
- **Phase 4:** AI Model Integration (use field data for predictions)

---

**Ready to build the frontend!** 🚀
