import {MapContainer,TileLayer,Marker,Rectangle,useMapEvents,useMap} from 'react-leaflet';
import L from 'leaflet';
import type {LatLngExpression} from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {useEffect} from 'react';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({iconRetinaUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',iconUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',shadowUrl:'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png'});

function ClickCapture({onPick}:{onPick:(lat:number,lng:number)=>void}){useMapEvents({click(e){onPick(e.latlng.lat,e.latlng.lng)}});return null}
function Recenter({center}:{center:[number,number]}){const map=useMap();useEffect(()=>{map.setView(center,map.getZoom())},[center,map]);return null}
export default function FieldMap({center,onPick,ndviTileUrl}:{center:[number,number];onPick:(lat:number,lng:number)=>void;ndviTileUrl?:string}){
 const c=center as LatLngExpression;
 return <div className="map-frame"><MapContainer center={c} zoom={7} scrollWheelZoom className="leaflet-map"><Recenter center={center}/><TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>{ndviTileUrl&&<TileLayer attribution="Google Earth Engine · Sentinel-2 NDVI" url={ndviTileUrl} opacity={.72} zIndex={350}/>}<Rectangle bounds={[[center[0]-.16,center[1]-.22],[center[0]+.16,center[1]+.22]]} pathOptions={{color:'#587c42',weight:2,fillColor:'#9ebd77',fillOpacity:.2}}/><Marker position={c}/><ClickCapture onPick={onPick}/></MapContainer><div className="map-label"><span className="live-dot"/> ANALYSIS POINT</div><div className="ndvi-legend"><span>{ndviTileUrl?'NDVI composite':'NDVI · illustrative scale'}</span><i/><div><small>Lower</small><small>Higher</small></div></div><div className="map-hint">{ndviTileUrl?'Sentinel-2 NDVI overlay':'OpenStreetMap base · click to reposition'}</div></div>
}
