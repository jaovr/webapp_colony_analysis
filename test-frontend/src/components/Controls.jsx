export default function Controls({ onImageSelect, onConvert }) {
    return (
        <div className="flex justify-center gap-4">
            <label className="btn btn-outline btn-primary">
                <input
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                            onImageSelect(e.target.files[0]);
                        }
                    }}
                />
                Selecionar Imagem
            </label>

            <button className="btn btn-primary" onClick={onConvert}>
                Converter
            </button>
        </div>
    );
}

