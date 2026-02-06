'use client';

import { GoogleMap, InfoWindow, Marker, useJsApiLoader } from '@react-google-maps/api';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { MESSAGES } from '@/constants';

export interface SpotLocation {
  name: string;
  lat: number;
  lng: number;
  originalIndex: number;
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
      originalIndex: number,
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
                originalIndex,
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

    /**
     * Searches for the geographic locations of all spots using Google Places API.
     *
     * Creates a temporary Google Map instance (via DOM element creation) to initialize
     * the PlacesService, which is required by the Google Maps API architecture.
     * The PlacesService cannot be instantiated without a Map or div element reference.
     *
     * Process:
     * 1. Creates a temporary DOM element and Map instance for PlacesService initialization
     * 2. Sequentially searches for each spot's location using the Places API
     * 3. Updates the state with found locations
     * 4. Calculates and sets the map center to the average position of all found locations
     * 5. Updates the searching state flag
     *
     * @remarks
     * DOM generation is necessary because `google.maps.places.PlacesService` requires
     * either a Map instance or an HTMLDivElement as a constructor parameter per Google Maps API specification.
     * The temporary map is only used for API initialization and not rendered to the UI.
     *
     * @returns {Promise<void>} A promise that resolves when all spot locations have been searched and state updated
     */
    /**
     * すべてのスポットの位置情報を検索し、地図上に表示するための処理を行います。
     *
     * @remarks
     * この関数は以下の処理を順次実行します：
     * 1. 検索中フラグを立てる
     * 2. Google Places APIを使用して各スポットの位置情報を検索
     * 3. 取得した位置情報を状態に保存
     * 4. すべてのスポットの平均座標を計算し、地図の中心位置を設定
     * 5. 検索中フラグを解除
     *
     * @returns Promise<void> - 非同期処理の完了を表すPromise
     *
     * @throws Google Places APIのエラーが発生した場合、個別のスポット検索は失敗する可能性がありますが、
     * 関数全体の実行は継続されます
     */
    const searchAllSpots = async () => {
      setIsSearching(true);

      const mapDiv = document.createElement('div');
      const tempMap = new google.maps.Map(mapDiv);
      const service = new google.maps.places.PlacesService(tempMap);

      const locationPromises = spots.map((spot, i) => searchSpotLocation(spot, i + 1, service));
      const results = await Promise.all(locationPromises);
      const locations = results.filter((loc): loc is SpotLocation => loc !== null);

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
        <p className="text-neutral-600">{MESSAGES.MAP_LOAD_ERROR}</p>
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
            <p className="text-neutral-600 text-sm">{MESSAGES.SEARCHING_SPOTS}</p>
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
              text: String(spot.originalIndex),
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
