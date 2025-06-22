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

const UserDashboard = () => {
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
      <Header title="Photo Server - Dashboard" />
      
      <Container>
        <TabContainer>
          <Tab 
            active={activeTab === 'upload'} 
            onClick={() => setActiveTab('upload')}
          >
            Upload Photos
          </Tab>
          <Tab 
            active={activeTab === 'my-photos'} 
            onClick={() => setActiveTab('my-photos')}
          >
            My Photos
          </Tab>
          <Tab 
            active={activeTab === 'global'} 
            onClick={() => setActiveTab('global')}
          >
            Shared Photos
          </Tab>
        </TabContainer>

        {activeTab === 'upload' && (
          <FileUpload 
            isAdmin={false} 
            onUploadComplete={handleUploadComplete}
          />
        )}

        {activeTab === 'my-photos' && (
          <PhotoGrid 
            title="My Photos" 
            isAdmin={false}
            showGlobal={false}
            onRefresh={handleRefresh}
            key={`personal-${refreshCounter}`}
          />
        )}

        {activeTab === 'global' && (
          <PhotoGrid 
            title="Shared Photos" 
            isAdmin={false}
            showGlobal={true}
            onRefresh={handleRefresh}
            key={`global-${refreshCounter}`}
          />
        )}
      </Container>
    </div>
  );
};

export default UserDashboard;
