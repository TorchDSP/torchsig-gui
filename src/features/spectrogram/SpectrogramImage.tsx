import { buildImageLink } from "@/api/api-slice";
import DataLoadingSpinner from "@/components/form-parts/DataLoadingSpinner";

// Contains the spectrogram image to display to the user
export default function SpectrogramContainer({ filename, hasLoaded, setHasLoaded }: { filename: string, hasLoaded: boolean, setHasLoaded: CallableFunction }) {
  // Return the spectrogram image
  return (
    <div className="d-flex justify-content-center align-items-center" style={{aspectRatio: 3 / 1}}>
      { hasLoaded && filename.length === 0 && <p>No Spectrogram Generated.</p> }
      { !hasLoaded && <DataLoadingSpinner /> }
      {/* next/image adds nothing here: the static export serves unoptimized images from a dynamic API URL */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={buildImageLink(filename)}
        alt="Spectrogram"
        fetchPriority="low"
        onLoad={() => setHasLoaded(true)}
        style={{
          height:"100%",
          width: "100%",
          objectFit: "contain",
          display: hasLoaded && filename.length > 0 ? "block" : "none"
        }}
      />
    </div>
  );
}