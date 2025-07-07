# Enhanced Action Engine Frontend - Coding Agent Prompt

## Project Context
You are implementing TODO #3.4: Enhanced Frontend Action Rules Management for an email management system. This involves creating a delightful and intuitive Action Engine frontend using inline category cards with action rules, following the detailed wireframe design in `memory-bank/action-engine-wireframes.md`.

## Core Design Principles
1. **Progressive Disclosure**: Start simple, reveal complexity on demand
2. **Visual Hierarchy**: Clear distinction between categories and their actions
3. **Contextual Intelligence**: Show affected email counts in real-time
4. **Delightful Interactions**: Smooth animations and immediate feedback
5. **Trust-Building**: Transparent preview and safety controls

## Implementation Approach

### Phase-Based Development
The implementation is broken into 5 phases to ensure quality and maintainability:

1. **Phase 3.4.1**: Core Category Card Enhancement
2. **Phase 3.4.2**: Action Rule Configuration Modal
3. **Phase 3.4.3**: Action Preview Dashboard
4. **Phase 3.4.4**: API Integration & State Management
5. **Phase 3.4.5**: Polish & Optimization

### Key Technical Requirements

#### Frontend Stack
- **Framework**: Next.js 14 with React Server Components
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Context + hooks
- **API**: RESTful endpoints with TypeScript types
- **Testing**: Playwright for E2E, Jest for unit tests

#### Backend Integration
- **Action Engine APIs**: Already implemented in TODO #3.2 and #3.3
- **Endpoints**: Action rule management and proposed actions
- **Models**: EmailCategory with action fields, ProposedAction model

## Detailed Implementation Guidelines

### Phase 3.4.1: Core Category Card Enhancement

#### 1. Update Category Card Component
**File**: `frontend/src/components/ui/category-rule-forms.tsx`

**Requirements**:
- Add action rule display section to each category card
- Implement progressive disclosure for rule details
- Add visual indicators for rule status (active, disabled, pending)
- Maintain existing category management functionality

**Key Features**:
```typescript
interface CategoryCardProps {
  category: EmailCategory;
  actionRules: ActionRule[];
  onEditRule: (ruleId: string) => void;
  onPreviewRule: (ruleId: string) => void;
  onToggleRule: (ruleId: string, enabled: boolean) => void;
}
```

**Visual Elements**:
- Action rule section with 🎯 icon
- Status indicators with appropriate colors
- Affected email counts and next action timing
- Edit/Preview/Disable buttons for each rule
- "Add Another Rule" button for multiple rules

#### 2. Create Action Rule Display Component
**File**: `frontend/src/components/ui/action-rule-display.tsx`

**Requirements**:
- Display action type with icons (📤 Archive, 🗑️ Trash)
- Show affected email counts and next action timing
- Include edit/preview/disable buttons for each rule
- Handle multiple rules per category

**Component Structure**:
```typescript
interface ActionRuleDisplayProps {
  rules: ActionRule[];
  categoryId: string;
  onEdit: (ruleId: string) => void;
  onPreview: (ruleId: string) => void;
  onToggle: (ruleId: string, enabled: boolean) => void;
  onAddRule: () => void;
}
```

#### 3. Add Smart Defaults
**File**: `frontend/src/components/ui/action-rule-suggestions.tsx`

**Requirements**:
- Suggest common rule patterns based on category type
- Show "Add Your First Rule" for categories without rules
- Display rule templates for quick setup

**Smart Suggestions**:
- **Promotions**: "Trash after 3 days" or "Archive after 1 day if not opened"
- **Social**: "Archive after 7 days"
- **Updates**: "Archive after 14 days"
- **Primary**: "Archive after 30 days"

### Phase 3.4.2: Action Rule Configuration Modal

#### 1. Create Configuration Modal
**File**: `frontend/src/components/ui/action-rule-modal.tsx`

**Requirements**:
- Implement action type selector with descriptions
- Add timing configuration with conditional logic options
- Include real-time preview of affected emails
- Add safety settings panel with user preferences

**Modal Structure**:
```typescript
interface ActionRuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  categoryId: string;
  initialRule?: ActionRule;
  onSave: (rule: ActionRule) => void;
}
```

**Form Sections**:
1. **Action Type**: Radio buttons with icons and descriptions
2. **Timing**: Days input with conditional logic checkboxes
3. **Preview**: Real-time affected email count and samples
4. **Safety Settings**: User preference toggles

#### 2. Build Form Components
**File**: `frontend/src/components/ui/action-rule-form.tsx`

**Requirements**:
- Implement action type radio buttons with icons
- Add timing input with smart validation
- Create conditional logic checkboxes
- Build safety settings toggles

**Form Validation**:
- Minimum delay: 1 day
- Maximum delay: 365 days
- Required fields: action type, delay days
- Conditional logic: at least one condition selected

#### 3. Add Real-time Preview
**File**: `frontend/src/components/ui/action-preview.tsx`

**Requirements**:
- Show live count of affected emails
- Display sample email subjects and senders
- Show next action scheduling information
- Include "Preview Full List" functionality

### Phase 3.4.3: Action Preview Dashboard

#### 1. Create Preview Dashboard
**File**: `frontend/src/app/action-preview/page.tsx`

**Requirements**:
- Build summary panel with action details and counts
- Implement email list with individual controls
- Add bulk action capabilities with selection

#### 2. Build Email Preview Components
**File**: `frontend/src/components/ui/email-preview-item.tsx`

**Requirements**:
- Display email subject, sender, and age
- Show action that will be taken
- Include individual exclude/include controls
- Add "View Email" link for context

#### 3. Implement Bulk Operations
**File**: `frontend/src/components/ui/bulk-actions-bar.tsx`

**Requirements**:
- Add select all/deselect all functionality
- Implement bulk exclude/include operations
- Show count of selected items
- Add execute/schedule buttons

### Phase 3.4.4: API Integration & State Management

#### 1. Extend API Layer
**File**: `frontend/src/lib/api.ts`

**New Endpoints**:
```typescript
// Action Rule Management
getActionRules(categoryId: string): Promise<ActionRule[]>;
createActionRule(categoryId: string, rule: ActionRuleRequest): Promise<ActionRule>;
updateActionRule(ruleId: string, rule: ActionRuleRequest): Promise<ActionRule>;
deleteActionRule(ruleId: string): Promise<void>;
toggleActionRule(ruleId: string, enabled: boolean): Promise<ActionRule>;

// Action Preview
getActionPreview(ruleId: string): Promise<ActionPreview>;
executeAction(ruleId: string, emailIds?: string[]): Promise<void>;
scheduleAction(ruleId: string, scheduledAt: Date): Promise<void>;
```

#### 2. Create State Management
**File**: `frontend/src/lib/action-engine-context.tsx`

**Context Structure**:
```typescript
interface ActionEngineContextType {
  actionRules: Record<string, ActionRule[]>;
  loading: boolean;
  error: string | null;
  refreshRules: (categoryId?: string) => Promise<void>;
  updateRule: (ruleId: string, updates: Partial<ActionRule>) => Promise<void>;
  createRule: (categoryId: string, rule: ActionRuleRequest) => Promise<void>;
  deleteRule: (ruleId: string) => Promise<void>;
}
```

#### 3. Add Error Handling
**File**: `frontend/src/components/ui/error-boundary.tsx`

**Requirements**:
- Implement graceful degradation for API failures
- Add user-friendly error messages
- Include retry mechanisms for failed operations

### Phase 3.4.5: Polish & Optimization

#### 1. Add Animations & Transitions
- Smooth hover effects for category cards
- Loading states with skeleton screens
- Smooth modal transitions
- Micro-interactions for button states

#### 2. Optimize Performance
- Lazy loading for email previews
- Debounced validation for form inputs
- Optimize re-renders with React.memo
- Virtual scrolling for large email lists

#### 3. Enhance Accessibility
- Proper ARIA labels and roles
- Keyboard navigation
- Screen reader compatibility
- High contrast mode support

#### 4. Add Delightful Features
- Toast notifications for actions
- Confirmation dialogs for destructive actions
- Success animations for completed actions
- Keyboard shortcuts for power users

## Development Workflow

### 1. Start with Phase 3.4.1
- Begin by enhancing existing category cards
- Focus on visual hierarchy and progressive disclosure
- Ensure existing functionality remains intact

### 2. Implement Incrementally
- Build and test each component individually
- Use TypeScript for type safety
- Write tests as you develop

### 3. Follow Design Principles
- Reference wireframes in `memory-bank/action-engine-wireframes.md`
- Prioritize user trust and control
- Maintain delightful interactions

### 4. Test Thoroughly
- Unit tests for each component
- Integration tests for API calls
- E2E tests for user workflows
- Accessibility testing

## Success Criteria

### User Experience
- Users feel confident and in control of automated actions
- Interface is intuitive and requires minimal learning
- Actions are transparent and previewable
- Performance is excellent across all devices

### Technical Quality
- All components are properly typed with TypeScript
- Comprehensive test coverage
- Accessibility compliance
- Performance optimization
- Error handling and graceful degradation

### Integration
- Seamless integration with existing category management
- Proper integration with backend Action Engine APIs
- Consistent state management across components
- Real-time updates and synchronization

## Getting Started

1. **Read the wireframes**: Review `memory-bank/action-engine-wireframes.md` thoroughly
2. **Understand the backend**: Review TODO #3.2 and #3.3 implementations
3. **Start with Phase 3.4.1**: Enhance category cards first
4. **Build incrementally**: Complete each phase before moving to the next
5. **Test continuously**: Write tests as you develop

Remember: The goal is to create a delightful, trustworthy, and intuitive email automation experience that makes users feel confident and in control. 