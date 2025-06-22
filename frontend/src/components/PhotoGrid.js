import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const GridContainer = styled.div`
  background-color: #1e1e1e;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
`;

const GridTitle = styled.h3`
  margin-top: 0;
  margin-bottom: 1rem;
  color: #e0e0e0;
`;

const Controls = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
`;

const SearchInput = styled.input`
  padding: 0.5rem;
  border: 1px solid #333;
  border-radius: 6px;
  background-color: #2a2a2a;
  color: #e0e0e0;
  width: 200px;

  &:focus {
    outline: none;
    border-color: #5e60ce;
  }
`;

const FilterSelect = styled.select`
  padding: 0.5rem;
  border: 1px solid #333;
  border-radius: 6px;
  background-color: #2a2a2a;
  color: #e0e0e0;

  &:focus {
    outline: none;
    border-color: #5e60ce;
  }
`;

const ActionButton = styled.button`
  background-color: ${props => props.danger ? '#dc3545' : '#5e60ce'};
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: ${props => props.danger ? '#c82333' : '#4c4fb8'};
  }

  &:disabled {
    background-color: #333;
    cursor: not-allowed;
  }
`;

const PhotosGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const PhotoCard = styled.div`
  background-color: #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease;
  cursor: pointer;
  position: relative;

  &:hover {
    transform: translateY(-2px);
  }
`;

const PhotoImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
`;

const VideoThumbnail = styled.div`
  width: 100%;
  height: 200px;
  background-color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &::before {
    content: '▶';
    font-size: 2rem;
    color: #5e60ce;
  }
`;

const PhotoInfo = styled.div`
  padding: 0.75rem;
`;

const PhotoName = styled.div`
  color: #e0e0e0;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  word-break: break-word;
`;

const PhotoDate = styled.div`
  color: #b0b0b0;
  font-size: 0.8rem;
`;

const CheckboxContainer = styled.div`
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  z-index: 2;
`;

const Checkbox = styled.input`
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #b0b0b0;
  padding: 2rem;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  padding: 1rem;
  background-color: rgba(255, 107, 107, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 107, 107, 0.3);
  margin-bottom: 1rem;
`;

const PhotoGrid = ({ title, isAdmin = false, showGlobal = false, onRefresh }) => {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPhotos, setSelectedPhotos] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadPhotos();
  }, [showGlobal]);

  const loadPhotos = async () => {
    try {
      setLoading(true);
      setError('');
      
      const endpoint = showGlobal ? '/photos/global' : '/photos';
      const response = await axios.get(endpoint);
      
      // Handle different response formats
      if (showGlobal) {
        // Global photos endpoint returns array directly
        setPhotos(Array.isArray(response.data) ? response.data : []);
      } else {
        // Regular photos endpoint returns paginated response with photos array
        setPhotos(Array.isArray(response.data.photos) ? response.data.photos : []);
      }
    } catch (error) {
      console.error('Failed to load photos:', error);
      setError('Failed to load photos');
      setPhotos([]); // Ensure photos is always an array
    } finally {
      setLoading(false);
    }
  };

  const filteredPhotos = (photos || []).filter(photo => {
    const matchesSearch = photo.filename.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || 
      (filterType === 'images' && photo.filename.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i)) ||
      (filterType === 'videos' && photo.filename.match(/\.(mp4|mov|avi|mkv|webm)$/i));
    
    return matchesSearch && matchesType;
  });

  const handlePhotoSelect = (photoId) => {
    setSelectedPhotos(prev => 
      prev.includes(photoId) 
        ? prev.filter(id => id !== photoId)
        : [...prev, photoId]
    );
  };

  const handleSelectAll = () => {
    if (selectedPhotos.length === filteredPhotos.length) {
      setSelectedPhotos([]);
    } else {
      setSelectedPhotos(filteredPhotos.map(photo => photo.id));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedPhotos.length === 0) return;
    
    if (!window.confirm(`Delete ${selectedPhotos.length} selected photos?`)) {
      return;
    }

    try {
      const deletePromises = selectedPhotos.map(photoId => {
        const endpoint = showGlobal ? `/photos/global/${photoId}` : `/photos/${photoId}`;
        return axios.delete(endpoint);
      });

      await Promise.all(deletePromises);
      setSelectedPhotos([]);
      loadPhotos();
      
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Failed to delete photos:', error);
      setError('Failed to delete some photos');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const isVideo = (filename) => {
    return filename.match(/\.(mp4|mov|avi|mkv|webm)$/i);
  };

  const getPhotoUrl = (photo) => {
    const baseUrl = showGlobal ? '/uploads/global' : '/uploads';
    return `${baseUrl}/${photo.filename}`;
  };

  const getThumbnailUrl = (photo) => {
    if (photo.thumbnail_path) {
      return `/uploads/${photo.thumbnail_path}`;
    }
    return getPhotoUrl(photo);
  };

  if (loading) {
    return (
      <GridContainer>
        <LoadingMessage>Loading photos...</LoadingMessage>
      </GridContainer>
    );
  }

  return (
    <GridContainer>
      <GridTitle>{title}</GridTitle>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <Controls>
        <SearchInput
          type="text"
          placeholder="Search photos..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        
        <FilterSelect 
          value={filterType} 
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="all">All Files</option>
          <option value="images">Images Only</option>
          <option value="videos">Videos Only</option>
        </FilterSelect>
        
        {filteredPhotos.length > 0 && (
          <>
            <ActionButton onClick={handleSelectAll}>
              {selectedPhotos.length === filteredPhotos.length ? 'Deselect All' : 'Select All'}
            </ActionButton>
            
            {selectedPhotos.length > 0 && (
              <ActionButton danger onClick={handleBulkDelete}>
                Delete Selected ({selectedPhotos.length})
              </ActionButton>
            )}
          </>
        )}
      </Controls>

      {filteredPhotos.length === 0 ? (
        <LoadingMessage>No photos found</LoadingMessage>
      ) : (
        <PhotosGrid>
          {filteredPhotos.map((photo) => (
            <PhotoCard key={photo.id}>
              <CheckboxContainer>
                <Checkbox
                  type="checkbox"
                  checked={selectedPhotos.includes(photo.id)}
                  onChange={() => handlePhotoSelect(photo.id)}
                />
              </CheckboxContainer>
              
              {isVideo(photo.filename) ? (
                <VideoThumbnail />
              ) : (
                <PhotoImage
                  src={getThumbnailUrl(photo)}
                  alt={photo.filename}
                  loading="lazy"
                />
              )}
              
              <PhotoInfo>
                <PhotoName>{photo.filename}</PhotoName>
                <PhotoDate>{formatDate(photo.upload_date)}</PhotoDate>
              </PhotoInfo>
            </PhotoCard>
          ))}
        </PhotosGrid>
      )}
    </GridContainer>
  );
};

export default PhotoGrid;
