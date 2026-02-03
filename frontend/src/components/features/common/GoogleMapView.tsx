'use client';

import { GoogleMap, InfoWindow, Marker, useJsApiLoader } from '@react-google-maps/api';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export interface SpotLocation {
  name: string;
  lat: number;
  lng: number;
}

export interface GoogleMapViewProps {
  spots: string[];
  destination?: string;
  className?: string;
  height?: string;
}

const libraries: 'places'[] = ['places'];

const defaultMapContainerStyle = {
  width: '100%',
  borderRadius: '0.75rem',
};

const defaultCenter = {
  lat: 35.6762,
  lng: 139.6503,
};

const defaultZoom = 12;

export function GoogleMapView({
  spots,
  destination,
  className = '',
  height = '400px',
}: GoogleMapViewProps) {
  const [spotLocations, setSpotLocations] = useState<SpotLocation[]>([]);
  const [selectedSpot, setSelectedSpot] = useState<SpotLocation | null>(null);
  const [mapCenter, setMapCenter] = useState(defaultCenter);
  const [isSearching, setIsSearching] = useState(false);

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  const searchSpotLocation = useCallback(
    async (
      spotName: string,
      service: google.maps.places.PlacesService
    ): Promise<SpotLocation | null> => {
      const searchQuery = destination ? `${spotName} ${destination}` : spotName;

      return new Promise(resolve => {
        const request: google.maps.places.TextSearchRequest = {
          query: searchQuery,
        };

        service.textSearch(request, (results, status) => {
          if (
            status === google.maps.places.PlacesServiceStatus.OK &&
            results &&
            results.length > 0
          ) {
            const place = results[0];
            if (place.geometry?.location) {
              resolve({
                name: spotName,
                lat: place.geometry.location.lat(),
                lng: place.geometry.location.lng(),
              });
              return;
            }
          }
          resolve(null);
        });
      });
    },
    [destination]
  );

  const mapContainerStyle = useMemo(
    () => ({
      ...defaultMapContainerStyle,
      height,
    }),
    [height]
  );

  useEffect(() => {
    if (!isLoaded || spots.length === 0) return;

    const searchAllSpots = async () => {
      setIsSearching(true);

      const mapDiv = document.createElement('div');
      const tempMap = new google.maps.Map(mapDiv);
      const service = new google.maps.places.PlacesService(tempMap);

      const locations: SpotLocation[] = [];

      for (const spot of spots) {
        const location = await searchSpotLocation(spot, service);
        if (location) {
          locations.push(location);
        }
      }

      setSpotLocations(locations);

      if (locations.length > 0) {
        const avgLat = locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length;
        const avgLng = locations.reduce((sum, loc) => sum + loc.lng, 0) / locations.length;
        setMapCenter({ lat: avgLat, lng: avgLng });
      }

      setIsSearching(false);
    };

    searchAllSpots();
  }, [isLoaded, spots, searchSpotLocation]);

  const handleMarkerClick = useCallback((spot: SpotLocation) => {
    setSelectedSpot(spot);
  }, []);

  const handleInfoWindowClose = useCallback(() => {
    setSelectedSpot(null);
  }, []);

  if (loadError) {
    return (
      <div
        className={`flex items-center justify-center rounded-xl bg-neutral-100 ${className}`}
        style={{ height }}
      >
        <p className="text-neutral-600">マップの読み込みに失敗しました</p>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div
        className={`flex items-center justify-center rounded-xl bg-neutral-100 ${className}`}
        style={{ height }}
      >
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {isSearching && (
        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-white/70">
          <div className="flex flex-col items-center gap-2">
            <LoadingSpinner size="md" />
            <p className="text-neutral-600 text-sm">スポットを検索中...</p>
          </div>
        </div>
      )}
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={mapCenter}
        zoom={defaultZoom}
        options={{
          streetViewControl: false,
          mapTypeControl: false,
          fullscreenControl: true,
          zoomControl: true,
        }}
      >
        {spotLocations.map((spot, index) => (
          <Marker
            key={`${spot.name}-${index}`}
            position={{ lat: spot.lat, lng: spot.lng }}
            label={{
              text: String(index + 1),
              color: 'white',
              fontWeight: 'bold',
            }}
            onClick={() => handleMarkerClick(spot)}
          />
        ))}

        {selectedSpot && (
          <InfoWindow
            position={{ lat: selectedSpot.lat, lng: selectedSpot.lng }}
            onCloseClick={handleInfoWindowClose}
          >
            <div className="p-1">
              <p className="font-semibold text-neutral-900">{selectedSpot.name}</p>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
}
