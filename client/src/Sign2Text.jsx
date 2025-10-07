import React, { useState, useRef, useEffect } from 'react'
import { createSocketConnection, sendImageFile } from './handler'

import {
    FaPlay,
    FaStop,
    FaCopy,
    FaVideo,
    FaFileUpload,
} from 'react-icons/fa'
import {
    MessageSquare,
    Loader2,
    Download
} from 'lucide-react'

const Sign2Text = () => {
    // Core processing states
    const [isProcessing, setIsProcessing] = useState(false)
    const [isStopping, setIsStopping] = useState(false)
    const [translatedText, setTranslatedText] = useState('')
    const [confidence, setConfidence] = useState(0)

    // WebSocket & processing
    const [captureIntervalId, setCaptureIntervalId] = useState(null)
    const socketRef = useRef(null)

    // Global camera/file states
    const [uploadFile, setUploadFile] = useState(null)
    const [uploadFileUrl, setUploadFileUrl] = useState(null)
    const [uploadFileType, setUploadFileType] = useState('video')
    const [isLiveCameraOpen, setIsLiveCameraOpen] = useState(false)
    const videoRef = useRef(null)

    // Camera settings
    const [resolution, setResolution] = useState({ width: 640, height: 480 }) // Default resolution
    const [fps, setFps] = useState(4) // Frames per second for processing
    const [mirror, setMirror] = useState(false)

    const toggleRecording = () => {
        if (!isLiveCameraOpen) {
            // Starting live camera

            if (uploadFileUrl) {
                // Clear uploaded video when starting live camera
                URL.revokeObjectURL(uploadFileUrl)
                setUploadFileUrl(null)
                setUploadFileType('video')
            }

            navigator.mediaDevices.getUserMedia({ video: true, width: resolution.width, height: resolution.height })
                .then(stream => {
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream
                    }
                })
                .catch(err => {
                    console.error("Error accessing camera: ", err)
                })

            clearText()
        }
        else {
            // Stop all video tracks
            if (videoRef.current && videoRef.current.srcObject) {
                const tracks = videoRef.current.srcObject.getTracks()
                tracks.forEach(track => track.stop())
                videoRef.current.srcObject = null
            }
            setIsProcessing(false)
        }
        setIsLiveCameraOpen(!isLiveCameraOpen)
    }

    const establishSocketConnection = () => {
        // Create Socket connection
        socketRef.current = createSocketConnection(socketRef)

        // Wait for socket to open
        socketRef.current.onopen = () => {
            console.log("WebSocket connected")
            const intervalId = setInterval(sendFrame, 1000 / fps)
            setCaptureIntervalId(intervalId)
        }

        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data)
            processTranslatedText(data.result)
        }

        socketRef.current.onerror = (error) => {
            console.error("WebSocket error: ", error)
            // setIsProcessing(false)
            socketRef.current.close()
        }

        socketRef.current.onclose = () => {
            console.log("WebSocket disconnected")
            if (captureIntervalId) {
                clearInterval(captureIntervalId)
                setCaptureIntervalId(null)
            }
            setIsProcessing(false)
        }
    }

    // File handling
    const handleFileUpload = (event) => {
        const file = event.target.files[0]

        if (file) {
            // Clean up previous video URL to prevent memory leaks
            if (uploadFileUrl) {
                URL.revokeObjectURL(uploadFileUrl)
            }

            // Create a URL for the file
            const url = URL.createObjectURL(file)
            setUploadFileUrl(url)

            setUploadFile(file)
            setUploadFileType(file.type.startsWith('image/') ? 'image' : 'video')

            clearText()
        }
    }

    const sendFrame = () => {
        if (!videoRef.current || !socketRef.current) {
            console.warn("Video or Socket not available")
            return;
        }
        if (socketRef.current.readyState !== WebSocket.OPEN) {
            console.warn("WebSocket is not open")
            return;
        }

        const video = videoRef.current
        const canvas = document.createElement('canvas')

        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        let frameData = canvas.toDataURL('image/jpeg', 0.8);

        // Send frameData to backend for processing
        socketRef.current.send(frameData)
    }

    // Start real-time or image/video translation
    const startTranslation = async () => {
        clearText()
        setIsProcessing(true)

        // For Real-time Camera / Video File
        if (uploadFileType === 'video' && !captureIntervalId) {
            // If video file is uploaded, restart the video
            if (uploadFile) {
                videoRef.current.currentTime = 0
                videoRef.current.play()
            }

            establishSocketConnection()
        }
        else if (uploadFile && uploadFileType === 'image') {
            // For Uploaded Image File
            const result = await sendImageFile(uploadFile)
            processTranslatedText(result)

            setIsProcessing(false)
        }
    }

    // Stop translation processing
    const stopTranslation = () => {
        if (captureIntervalId) {
            clearInterval(captureIntervalId)
            setCaptureIntervalId(null)
        }
        setTimeout(() => {
            if (socketRef.current) {
                socketRef.current.close()
                socketRef.current = null
                setIsProcessing(false)
                setIsStopping(false)
            }
        }, 5000) // Delay to ensure all generated text is received before closing

        setIsStopping(true)
    }

    // Process Translation Results
    const processTranslatedText = (data) => {
        if (data && data.text) {
            const text = data.text.trim().toLowerCase()
            setTranslatedText(prev => prev + " " + text)

            const word_conf = data.word_confidence || 0
            const sentence_conf = data.sentence_confidence || 0

            const max_conf = Math.max(word_conf, sentence_conf).toFixed(4)
            setConfidence(Number(max_conf) * 100)
        }
    }

    const clearText = () => {
        setTranslatedText('')
        setConfidence(0)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 py-8">
            <div className="max-w-7xl mx-auto px-4">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                        Sign Language to Text Translator
                    </h1>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        Position yourself in front of the camera and start signing. Our AI will translate your gestures into text in real-time.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Camera Section */}
                    <div className="space-y-6">
                        <CameraFeedSection
                            isLiveCameraOpen={isLiveCameraOpen} toggleRecording={toggleRecording}
                            videoRef={videoRef}
                            startTranslation={startTranslation} stopTranslation={stopTranslation}
                            handleFileUpload={handleFileUpload}
                            uploadFileUrl={uploadFileUrl}
                            uploadFileType={uploadFileType}
                            isProcessing={isProcessing} isStopping={isStopping}
                            mirror={mirror}
                        />

                        {/* Camera Settings */}
                        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Camera Settings</h3>
                            <div className="space-y-4 flex flex-wrap gap-4 justify-around items-center">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Resolution</label>
                                    <select
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        value={`${resolution.width}x${resolution.height}`}
                                        onChange={(e) => {
                                            const [width, height] = e.target.value.split('x').map(Number)
                                            setResolution({ width, height })
                                        }}
                                    >
                                        <option value={'1280x720'}>1280x720 (HD)</option>
                                        <option value={'1920x1080'}>1920x1080 (Full HD)</option>
                                        <option value={'640x480'}>640x480 (Standard)</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Frame Rate</label>
                                    <select
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        value={fps}
                                        onChange={(e) => setFps(Number(e.target.value))}
                                    >
                                        <option value={3}>3 FPS</option>
                                        <option value={4}>4 FPS</option>
                                        <option value={5}>5 FPS</option>
                                    </select>
                                </div>

                                {isLiveCameraOpen && (<div className="flex items-center">
                                    <input
                                        type="checkbox" id="mirrored"
                                        checked={mirror}
                                        onChange={() => setMirror(!mirror)}
                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    />
                                    <label htmlFor="mirrored" className="ml-2 text-sm text-gray-700">Mirror camera feed</label>
                                </div>)}
                            </div>
                        </div>
                    </div>

                    {/* Translation Results Section */}
                    <div className="space-y-6">
                        <TranslationResultsSection
                            translatedText={translatedText}
                            confidence={confidence}
                            isProcessing={isProcessing}
                            clearText={clearText}
                        />

                        {/* Tips */}
                        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200">
                            <h3 className="text-lg font-semibold text-gray-900 mb-3">📝 Tips for Better Recognition</h3>
                            <ul className="space-y-2 text-sm text-gray-700">
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Ensure good lighting and clear background
                                </li>
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Position hands clearly within the camera frame
                                </li>
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Sign at a moderate pace for better accuracy
                                </li>
                                <li className="flex items-start">
                                    <span className="text-blue-500 mr-2">•</span>
                                    Maintain consistent distance from camera
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

const CameraFeedSection = ({ isLiveCameraOpen, toggleRecording, videoRef, startTranslation, stopTranslation, handleFileUpload, uploadFileUrl, uploadFileType, isProcessing, isStopping, mirror }) => {

    return (
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Camera Feed</h2>
                <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${isLiveCameraOpen ? 'bg-red-500 animate-pulse' : 'bg-gray-300'}`}></div>
                    <span className="text-sm text-gray-600">
                        {isLiveCameraOpen ? 'Recording' : uploadFileUrl ? 'File Uploaded' : 'Stopped'}
                    </span>
                </div>
            </div>

            {/* Video Container */}
            <div className="relative aspect-video bg-gray-900 rounded-xl overflow-hidden mb-6">
                <video
                    ref={videoRef}
                    src={uploadFileUrl}
                    className="w-full h-full object-cover"
                    style={{
                        display: uploadFileType === 'video' ? 'block' : 'none',
                        transform: isLiveCameraOpen && mirror ? 'scale(-1,1)' : 'none'
                    }}
                    onEnded={stopTranslation}
                    autoPlay muted
                    playsInline
                />

                <img
                    src={uploadFileUrl}
                    alt="Uploaded Image"
                    className="w-full h-full object-contain object-center"
                    style={{ display: uploadFileType !== 'video' ? 'block' : 'none' }}
                />

                {/* Overlay for when camera is not active */}
                {!isLiveCameraOpen && !uploadFileUrl && (
                    <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
                        <div className="text-center text-white">
                            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <FaVideo className="w-8 h-8" />
                            </div>
                            <p className="text-lg font-medium">Camera Preview</p>
                            <p className="text-sm text-gray-300">Click Start Live Camera to begin</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Controls */}
            <div className="flex flex-wrap gap-4">
                <button
                    onClick={toggleRecording}
                    className={`flex-1 px-6 py-3 rounded-xl font-semibold text-lg transition-all duration-200 ${isLiveCameraOpen
                        ? 'bg-red-500 hover:bg-red-600 text-white'
                        : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white'
                        }`}
                >
                    {isLiveCameraOpen ? (
                        <span className="flex items-center justify-center">
                            <FaStop className="w-5 h-5 mr-2" />
                            Stop Live Camera
                        </span>
                    ) : (
                        <span className="flex items-center justify-center">
                            <FaPlay className="w-5 h-5 mr-2" />
                            Start Live Camera
                        </span>
                    )}
                </button>

                <button
                    className="relative flex-1 px-6 py-3 bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl font-semibold transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    disabled={isLiveCameraOpen}
                >
                    <input
                        type="file" accept="video/*,image/*"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={handleFileUpload}
                        disabled={isLiveCameraOpen}
                    />

                    <span className="flex items-center justify-center">
                        <FaFileUpload className="w-5 h-5 mr-2" />
                        Upload Video/Image
                    </span>
                </button>


                {!isProcessing && (<button
                    onClick={startTranslation}
                    disabled={!isLiveCameraOpen && !uploadFileUrl}
                    className="px-6 py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition-all duration-200"
                >
                    Translate
                </button>)}

                {isProcessing && (<button
                    onClick={stopTranslation}
                    disabled={isStopping}
                    className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-xl font-semibold transition-all duration-200 disabled:bg-gray-300"
                >
                    Stop
                </button>)}
            </div>
        </div>
    )
}

const TranslationResultsSection = ({ translatedText, confidence, isProcessing, clearText }) => {
    const [copied, setCopied] = useState(false)
    const [saved, setSaved] = useState(false)

    const copyText = () => {
        if (translatedText) {
            navigator.clipboard.writeText(translatedText)

            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        }
    }

    const saveTextAsFile = () => {
        if (translatedText) {
            console.log("Text saved: ", translatedText)

            setSaved(true)
            setTimeout(() => setSaved(false), 2000)
        }
    }

    useEffect(() => {
        setCopied(false)
        setSaved(false)
    }, [translatedText])

    return (
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Translation Results</h2>
                <button
                    onClick={clearText}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all duration-200"
                >
                    Clear
                </button>
            </div>

            {/* Translation Output */}
            <div className="min-h-[200px] p-4 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 mb-4">
                {translatedText ? (
                    <div>
                        <p className="text-lg text-gray-800 leading-relaxed">{translatedText}</p>
                        {confidence > 0 && (
                            <div className="mt-4 flex items-center">
                                <span className="text-sm text-gray-600 mr-2">Confidence:</span>
                                <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                                    <div
                                        className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-500"
                                        style={{ width: `${confidence}%` }}
                                    ></div>
                                </div>
                                <span className="text-sm font-medium text-gray-800">{confidence}%</span>
                            </div>
                        )}
                    </div>
                ) : isProcessing ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                            <Loader2 className="h-8 w-8 animate-spin text-blue-500 mx-auto mb-3" />
                            <p className="text-gray-600">Processing sign language...</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center justify-center h-full text-gray-500">
                        <div className="text-center">
                            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                            <p>Translated text will appear here</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
                <button
                    disabled={!translatedText}
                    className="flex-1 px-4 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-all duration-200"
                >
                    <span className="flex items-center justify-center" onClick={copyText}>
                        <FaCopy className="w-4 h-4 mr-2" />
                        {copied ? 'Copied!' : 'Copy Text'}
                    </span>
                </button>
                <button
                    disabled={!translatedText}
                    className="flex-1 px-4 py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-all duration-200"
                    onClick={saveTextAsFile}
                >
                    <span className="flex items-center justify-center">
                        <Download className="w-4 h-4 mr-2" />
                        {saved ? 'Saved!' : 'Save as File'}
                    </span>
                </button>
            </div>
        </div>
    )
}

export default Sign2Text
