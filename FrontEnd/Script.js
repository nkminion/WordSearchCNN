const UploadBtn = document.getElementById("Upload");
const FileInput = document.getElementById("FileInput");
const OutputPreview = document.getElementById("OutputPreview");
const StartBtn = document.getElementById("Start");
const InputPreview = document.getElementById("InputPreview");

let Puzzle = null;

UploadBtn.addEventListener("click", function()
{
	FileInput.click();
});

FileInput.addEventListener("change", async function()
{
	if (FileInput && FileInput.files[0])
	{
		UploadBtn.disabled = true;

		try
		{
			const ResizedImage = await ResizeImage(FileInput.files[0],800);

			InputPreview.src = ResizedImage;
			Puzzle = ResizedImage;

			StartBtn.disabled = false;
			UploadBtn.disabled = false;
		}
		catch (error)
		{
			console.error("Error: ",error);
		}
	}
});

StartBtn.addEventListener("click", async function()
{
	StartBtn.disabled = true;
	UploadBtn.disabled = true;

	const data = new FormData();
	data.append("InputFile",Puzzle);

	try
	{
		const Response = await fetch("/solve",{
			method: "POST",
			body: data
		});

		const Data = await Response.json();

		if (Data.Ret)
		{
			OutputPreview.src = Data.Image;
			alert("Puzzle Solved!");
			UploadBtn.disabled = false;
		}
	}
	catch (error)
	{
		console.error("Error: ",error);
	}
});

const ResizeImage = function(file,MaxHeight)
{
	return new Promise(function(resolve)
	{
		const Reader = new FileReader();
		Reader.onload = function(event)
		{
			const img = new Image();
			img.onload = function()
			{
				let width = img.width;
				let height = img.height;

				if (height > MaxHeight)
				{
					width *= (MaxHeight/height);
					height = MaxHeight;
				}

				const canvas = document.createElement('canvas');
				canvas.width = width;
				canvas.height = height;
				
				const ctx = canvas.getContext('2d');
				ctx.drawImage(img,0,0,width,height);

				const imgURL = canvas.toDataURL("image/png",0.8);
				resolve(imgURL);
			};
			img.src = event.target.result;
		};
		Reader.readAsDataURL(file);
	});
};

StartBtn.disabled = true;