import React, { useState } from 'react';
import styled from 'styled-components';
import Header from './Header';
import FileUpload from './FileUpload';
import PhotoGrid from './PhotoGrid';

const Container = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: 2rem;
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
`;

const Tab = styled.button`
  flex: 1;
  padding: 1rem;
  border: none;
  background-color: ${props => props.active ? '#5e60ce' : '#2a2a2a'};
  color: ${props => props.active ? 'white' : '#b0b0b0'};
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: ${props => props.active ? '#5e60ce' : '#333'};
  }
`;

const UserManagementSection = styled.div`
  background-color: #1e1e1e;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h3`
  margin-top: 0;
  margin-bottom: 1rem;
  color: #e0e0e0;
`;

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [refreshCounter, setRefreshCounter] = useState(0);

  const handleUploadComplete = () => {
    setRefreshCounter(prev => prev + 1);
  };

  const handleRefresh = () => {
    setRefreshCounter(prev => prev + 1);
  };

  return (
    <div>
      <Header title="Admin Panel - Photo Server" />
      
      <Container>
        <TabContainer>
          <Tab 
            active={activeTab === 'upload'} 
            onClick={() => setActiveTab('upload')}
          >
            Upload Photos
          </Tab>
          <Tab 
            active={activeTab === 'global'} 
            onClick={() => setActiveTab('global')}
          >
            Global Photos
          </Tab>
          <Tab 
            active={activeTab === 'users'} 
            onClick={() => setActiveTab('users')}
          >
            User Management
          </Tab>
        </TabContainer>

        {activeTab === 'upload' && (
          <>
            <FileUpload 
              isAdmin={true} 
              onUploadComplete={handleUploadComplete}
            />
            <PhotoGrid 
              title="My Photos" 
              isAdmin={true}
              showGlobal={false}
              onRefresh={handleRefresh}
              key={`personal-${refreshCounter}`}
            />
          </>
        )}

        {activeTab === 'global' && (
          <PhotoGrid 
            title="Global Photos (Shared)" 
            isAdmin={true}
            showGlobal={true}
            onRefresh={handleRefresh}
            key={`global-${refreshCounter}`}
          />
        )}

        {activeTab === 'users' && (
          <UserManagementSection>
            <SectionTitle>User Management</SectionTitle>
            <p style={{ color: '#b0b0b0' }}>
              User management functionality will be implemented here.
              Features will include:
            </p>
            <ul style={{ color: '#b0b0b0', marginLeft: '1rem' }}>
              <li>View all registered users</li>
              <li>Delete user accounts</li>
              <li>Reset user passwords</li>
              <li>View user upload statistics</li>
            </ul>
          </UserManagementSection>
        )}
      </Container>
    </div>
  );
};

export default AdminDashboard;
