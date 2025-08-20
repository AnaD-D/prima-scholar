// src/App.jsx
import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import ExcellenceDashboard from './components/ExcellenceDashboard';
import ScholarMentorship from './components/ScholarMentorship';
import DistinctionTracker from './components/DistinctionTracker';
import EliteResources from './components/EliteResources';
import { Award, Brain, Target, BookOpen } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';

const queryClient = new QueryClient();

function App() {
  const [studentId] = useState(() =>
    localStorage.getItem('prima_scholar_id') ||
    (() => {
      const id = 'scholar_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('prima_scholar_id', id);
      return id;
    })()
  );

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-blue-50">
        {/* Premium Header */}
        <header className="bg-white shadow-sm border-b border-indigo-100">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl">
                  <Award className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    Prima Scholar
                  </h1>
                  <p className="text-sm text-gray-600 font-medium">Where Excellence Meets Intelligence</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Premium Academic Excellence Platform</p>
                <p className="text-xs text-indigo-600 font-semibold">Transforming Good Students into Elite Scholars</p>
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8">
          <Tabs defaultValue="dashboard" className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-white shadow-sm">
              <TabsTrigger value="dashboard" className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                Excellence Dashboard
              </TabsTrigger>
              <TabsTrigger value="mentorship" className="flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Scholar Mentorship
              </TabsTrigger>
              <TabsTrigger value="distinctions" className="flex items-center gap-2">
                <Award className="h-4 w-4" />
                Distinction Tracker
              </TabsTrigger>
              <TabsTrigger value="resources" className="flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                Elite Resources
              </TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard">
              <ExcellenceDashboard studentId={studentId} />
            </TabsContent>
            <TabsContent value="mentorship">
              <ScholarMentorship studentId={studentId} />
            </TabsContent>
            <TabsContent value="distinctions">
              <DistinctionTracker studentId={studentId} />
            </TabsContent>
            <TabsContent value="resources">
              <EliteResources studentId={studentId} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;