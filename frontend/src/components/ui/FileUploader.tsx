'use client';

import { useCallback, useId, useRef, useState } from 'react';

import { FILE_UPLOADER } from '@/constants/ui';
import type { FileUploaderProps } from '@/types/ui';

const baseStyles = [
  'relative w-full',
  'border-2 border-dashed rounded-lg',
  'transition-all duration-200 ease-out',
  'cursor-pointer',
].join(' ');

const normalStyles = [
  'border-neutral-300 bg-neutral-50',
  'hover:border-primary-400 hover:bg-primary-50',
].join(' ');

const dragOverStyles = ['border-primary-500 bg-primary-100'].join(' ');

const disabledStyles = ['border-neutral-200 bg-neutral-100', 'cursor-not-allowed opacity-50'].join(
  ' '
);

const errorStyles = ['border-red-400 bg-red-50'].join(' ');

const contentStyles = [
  'flex flex-col items-center justify-center',
  'px-6 py-8',
  'text-center',
].join(' ');

const iconStyles = ['w-12 h-12 mb-4 text-primary-400'].join(' ');

const labelStyles = ['text-base font-medium text-neutral-700'].join(' ');

const hintStyles = ['mt-1 text-sm text-neutral-500'].join(' ');

const helpTextStyles = ['mt-2 text-sm text-neutral-500'].join(' ');

const errorMessageStyles = ['mt-2 text-sm text-red-600'].join(' ');

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`;
}

function UploadIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
      />
    </svg>
  );
}

export function FileUploader({
  accept,
  multiple = false,
  maxSize,
  onUpload,
  onError,
  disabled = false,
  className = '',
  label = FILE_UPLOADER.DEFAULT_LABEL,
  helpText,
}: FileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const id = useId();

  const validateFiles = useCallback(
    (files: File[]): { valid: File[]; errors: string[] } => {
      const valid: File[] = [];
      const errors: string[] = [];

      for (const file of files) {
        // Check file size
        if (maxSize && file.size > maxSize) {
          errors.push(FILE_UPLOADER.ERROR_FILE_SIZE_EXCEEDED(file.name, formatFileSize(maxSize)));
          continue;
        }

        // Check file type if accept is specified
        if (accept) {
          const acceptedTypes = accept.split(',').map(t => t.trim());
          const fileExtension = `.${file.name.split('.').pop()?.toLowerCase()}`;
          const mimeType = file.type;

          const isAccepted = acceptedTypes.some(acceptedType => {
            if (acceptedType.startsWith('.')) {
              // Extension check
              return fileExtension === acceptedType.toLowerCase();
            }
            if (acceptedType.endsWith('/*')) {
              // Wildcard MIME type (e.g., "image/*")
              const baseType = acceptedType.slice(0, -2);
              return mimeType.startsWith(baseType);
            }
            // Exact MIME type match
            return mimeType === acceptedType;
          });

          if (!isAccepted) {
            errors.push(FILE_UPLOADER.ERROR_INVALID_FILE_TYPE(file.name));
            continue;
          }
        }

        valid.push(file);
      }

      return { valid, errors };
    },
    [accept, maxSize]
  );

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;

      setErrorMessage(null);

      const fileArray = Array.from(files);
      const filesToProcess = multiple ? fileArray : [fileArray[0]];

      const { valid, errors } = validateFiles(filesToProcess);

      if (errors.length > 0) {
        const errorMsg = errors.join('\n');
        setErrorMessage(errorMsg);
        onError?.(errorMsg);
      }

      if (valid.length > 0) {
        onUpload(valid);
      }
    },
    [multiple, validateFiles, onUpload, onError]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent<HTMLButtonElement>) => {
      e.preventDefault();
      e.stopPropagation();
      if (!disabled) {
        setIsDragOver(true);
      }
    },
    [disabled]
  );

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLButtonElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);

      if (disabled) return;

      const { files } = e.dataTransfer;
      handleFiles(files);
    },
    [disabled, handleFiles]
  );

  const handleClick = useCallback(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  }, [disabled]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLButtonElement>) => {
      if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
        e.preventDefault();
        inputRef.current?.click();
      }
    },
    [disabled]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files);
      // Reset input value to allow selecting the same file again
      e.target.value = '';
    },
    [handleFiles]
  );

  const getDropzoneStyles = () => {
    if (disabled) return disabledStyles;
    if (errorMessage) return errorStyles;
    if (isDragOver) return dragOverStyles;
    return normalStyles;
  };

  const acceptHint = accept ? `${FILE_UPLOADER.ACCEPTED_FORMATS_PREFIX}${accept}` : undefined;

  const sizeHint = maxSize
    ? `${FILE_UPLOADER.MAX_SIZE_PREFIX}${formatFileSize(maxSize)}`
    : undefined;

  const hints = [acceptHint, sizeHint].filter(Boolean).join(' / ');

  return (
    <div className={className}>
      <button
        type="button"
        disabled={disabled}
        aria-describedby={errorMessage ? `${id}-error` : helpText ? `${id}-help` : undefined}
        className={[baseStyles, getDropzoneStyles()].join(' ')}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
      >
        <input
          ref={inputRef}
          id={id}
          type="file"
          accept={accept}
          multiple={multiple}
          disabled={disabled}
          onChange={handleInputChange}
          className="sr-only"
          aria-label={label}
        />
        <div className={contentStyles}>
          <UploadIcon className={iconStyles} />
          <p className={labelStyles}>{label}</p>
          <p className={hintStyles}>{FILE_UPLOADER.HINT_TEXT}</p>
          {hints && <p className={hintStyles}>{hints}</p>}
        </div>
      </button>
      {errorMessage && (
        <p id={`${id}-error`} className={errorMessageStyles} role="alert">
          {errorMessage}
        </p>
      )}
      {helpText && !errorMessage && (
        <p id={`${id}-help`} className={helpTextStyles}>
          {helpText}
        </p>
      )}
    </div>
  );
}
