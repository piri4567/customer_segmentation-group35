export default function ImageViewer({ src, alt, caption }) {
  return (
    <figure className="card overflow-hidden">
      <img
        src={src}
        alt={alt}
        className="w-full h-auto block bg-white"
      />
      {caption && (
        <figcaption className="px-4 py-3 text-xs text-slate-600 border-t border-slate-100 bg-slate-50">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
