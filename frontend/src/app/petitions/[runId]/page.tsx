import { TrackingView } from "@/components/petitions/TrackingView";
export default async function PetitionTrackingPage({params}:{params:Promise<{runId:string}>}){const {runId}=await params;return <TrackingView runId={runId}/>;}
