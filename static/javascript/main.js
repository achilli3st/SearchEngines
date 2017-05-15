<script type="text/javascript">
    function validate()
    {
        if (document.getElementById('advancedSearch').checked)
        {
            $('#ExactMatch').show();
            $('#ExactMatchText').show();
            $('#FuzzyMatchingFields').show();
            $('#FuzzyMatchingFieldsText').show();
            $('#FuzzyMatchingMultipleFieldsbyWeight').show();
            $('#FuzzyMatchingMultipleFieldsbyWeightText').show();
        }
        else
        {
            $('#ExactMatch').hide();
            $('#ExactMatchText').hide();
            $('#FuzzyMatchingFields').hide();
            $('#FuzzyMatchingFieldsText').hide();
            $('#FuzzyMatchingMultipleFieldsbyWeight').hide();
            $('#FuzzyMatchingMultipleFieldsbyWeightText').hide();
        }
    }

    function MultiFields()
    {
        if (document.getElementById('FuzzyMatchingMultipleFieldsbyWeight').checked)
        {
             $('#NumberofMultiOptions').show();
             $('#NumberofMultiOptionslabel').show();
        }
        else
        {
             $('#NumberofMultiOptions').hide();
             $('#NumberofMultiOptionslabel').hide();
        }
    }

    function NumberofOptions()
    {
        var NumberofMultiOptions = document.getElementById( "NumberofMultiOptions" );
        numberofOptions =Number(NumberofMultiOptions.options[ NumberofMultiOptions.selectedIndex ].value);
        console.log(numberofOptions)


        for(i=0;i<numberofOptions;i++)
        {
            var x = document.createElement("SELECT");
            var y ="MultiOptions";
            var w = y.concat(i);
            x.setAttribute("id",w);
            x.setAttribute("name", w)
            document.getElementById("searchform").appendChild(x);

            var a = document.createElement("SELECT");
            var b = "WeightOptions";
            var c = b.concat(i);
            a.setAttribute("id", c);
            a.setAttribute("name", c)
            document.getElementById("searchform").appendChild(a);
            /*
            var l = document.createElement("INPUT");
            var k = "MultiWeightText";
            var j = k.concat(i);
            l.setAttribute("type", "text");
            l.setAttribute("id", j);
            l.setAttribute("name", j)
            document.getElementById("searchform").appendChild(l);
            */
            for (f=0; f<optionArray.length; f++)
            {
                var z = document.createElement("option");
                z.setAttribute("value", optionArray[f]);
                var t = document.createTextNode(optionArray[f]);
                z.appendChild(t);
                document.getElementById(w).appendChild(z);
            }

            for (g=2; g<10; g++)
            {
                var e = document.createElement("option");
                e.setAttribute("value", g);
                var u = document.createTextNode(g);
                e.appendChild(u);
                document.getElementById(c).appendChild(e);
            }

        }
    }
</script>