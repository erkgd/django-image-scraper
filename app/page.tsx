"use client"
import { useState, FormEvent } from 'react'

export default function Home() {
  const [query, setQuery] = useState('')
  const [images, setImages] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  async function handleSearch(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/images/search/?query=${encodeURIComponent(query)}`)
      const data = await res.json()
      setImages(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <form onSubmit={handleSearch} className="flex mb-4">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search images..."
          className="flex-1 border p-2 rounded-l"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-500 text-white px-4 rounded-r hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {images.map(img => (
          <div key={img.url} className="border rounded overflow-hidden">
            <img src={img.thumbnail_url || img.url} alt={img.title} className="w-full h-32 object-cover" />
            <p className="p-2 text-sm truncate" title={img.title}>{img.title}</p>
          </div>
        ))}
      </div>
    </div>
  )
}