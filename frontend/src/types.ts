export type Crop='Rice'|'Wheat'|'Maize'|'Cotton'|'Soybean';
export type SeriesPoint={date:string;ndvi:number;evi:number;ndwi:number};
export type Analysis={provider:string;demo:boolean;data_notice:string;collection:string;cloud_threshold:number;imagery_status:string;ndvi_tile_url?:string;acquisitions:number;mean_cloud_percent:number;series:SeriesPoint[];features:Record<string,number>;region:string;latitude:number;longitude:number;crop:string;start_date:string;end_date:string};
export type Forecast={predicted_yield:number;unit:string;model:string;status:string;range:number[];range_note:string;features:{name:string;importance:number}[];demo:boolean;satellite_demo:boolean;data_notice:string;crop:string;region:string;vegetation:Record<string,number>;model_evaluation:{mae:number;rmse:number;r2:number;observations:number;evaluation:string}};
export type RequestData={latitude:number;longitude:number;region:string;crop:Crop;start_date:string;end_date:string;cloud_threshold:number};
